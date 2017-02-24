# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
import configparser
import os
import shutil
import glob
import functools
from enum import Enum, unique
from pathlib import Path
# library
import cv2
# Myapp library
from hsvcolor import HSVcolor
from classifier import Classifier

logger = getLogger('myapp.tweetbot')
if __name__ == "__main__":
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)
@unique
class ImageType(Enum):
    RAW = 1
    NUMBER = 2
    HINTS = 4
    PLAN = 8
    HINT_RAW = RAW | HINTS
    HINT_NUMBER = NUMBER | HINTS

class DataProcessor(object):
    def __init__(self, name, image_type):
        self.__name = name
        self.image_type = image_type
        self.color = None
        self.__hsv = None
        # todo:static fileds
        self.__contryMask = {'netzawar':(HSVcolor(175, 55, 0), HSVcolor(255, 255, 255)),
                             'casedria':(HSVcolor(53, 0, 0), HSVcolor(79, 255, 255)),
                             'geburand':(HSVcolor(120, 0, 100), HSVcolor(150, 255, 255)), 
                             'hordine':(HSVcolor(24, 0, 249), HSVcolor(30, 255, 255)),
                             'ielsord':(HSVcolor(79, 0, 0), HSVcolor(112, 255, 255))}
    @property
    def name(self):
        return self.__name
    @property
    def hsv(self):
        if self.__hsv is None:
            self.__hsv = cv2.cvtColor(self.color, cv2.COLOR_BGR2HSV)
        return self.__hsv
    def prepare(self):
        """
            @return color image
        """
        filename = self.name
        zoom = 2
        c = cv2.imread(filename)
        if c is None:
            logger.info("notfound:{0}".format(self.name))
            return c
        if (self.image_type == ImageType.NUMBER or self.image_type == ImageType.HINT_NUMBER):
            """
                number image size small.
                keypoints to 0
                image scall zooming
            """
            zoom = 10
        self.color = cv2.resize(c, (c.shape[1]*zoom, c.shape[0]*zoom), interpolation=cv2.INTER_CUBIC)
        return self.color
    def batch(self):
        """
            masking)
                step1:white color
                step2:color -> grayscale -> adaptiveThreshold -> binary
                step3:country color
                step4:fill min(500, height)
            @return binary image
        """
        if (self.image_type == ImageType.NUMBER or self.image_type == ImageType.HINT_NUMBER):
            return self.color
        white = self.__getWhiteMasking(self.hsv)
        binary = self.__binary_threshold(self.color)
        # white color
        binary = cv2.bitwise_and(binary, binary, mask=white)
        if self.image_type == ImageType.PLAN:
            height, width = self.color.shape[:2]
            cv2.rectangle(binary, (0, 0), (min(1000, width),height), (0,0,0), -1)
            print(self.color.shape[:2])
            return binary
        #fez country color mask pattern
        binary = self.bitwise_not(binary, self.__contryMask['netzawar'])
        binary = self.bitwise_not(binary, self.__contryMask['geburand'])
        binary = self.bitwise_not(binary, self.__contryMask['ielsord'])
        binary = self.bitwise_not(binary, self.__contryMask['casedria'])
        binary = self.bitwise_not(binary, self.__contryMask['hordine'])
        # １位より下を黒色で塗りつぶしてマスク。
        height, width = self.color.shape[:2]
        cv2.rectangle(binary, (0, min(500, height)), (width,height), (0,0,0), -1)
        return binary
    def bitwise_not(self, binary, mask_range):
        lower, upper = mask_range
        return cv2.bitwise_not(binary, binary, mask=self.__inRange(self.hsv, lower, upper))
    def __getWhiteMasking(self, hsv):
        sensitivity = 15
        lower = HSVcolor(0, 0, 255 - sensitivity)
        upper = HSVcolor(255, sensitivity, 255)
        return self.__inRange(hsv, lower, upper)
    def __inRange(self, hsv, lower, upper):
        return cv2.inRange(hsv, lower.to_np(), upper.to_np())
    def __binary_threshold(self, img):
        grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(grayscale
                    , 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 3)
        return thresh
class country(object):
    def __init__(self, config):
        self.hints = config['WORK_FOLDER']['HINTS']
        d = dict()
        names = config['COUNTRY']['NAMES'].split('|')
        for ele in names:
           c = ele.split(":")
           d[c[0]] = c[1]
        self.names = d
        self.detector = cv2.AKAZE_create()
        self.classifier = Classifier()
        self.numberclassifier = Classifier()
        self.__load(self.classifier, ImageType.HINT_RAW)
        for i in range(10):
            self.__load(self.numberclassifier, ImageType.HINT_NUMBER, i)
        
    
    def __load(self, classifier, image_type, n=None):
        """
            loading descriptors image and label
        """
        loadPath = Path(self.hints)
        if n is not None:
            loadPath  = Path(self.hints, 'number', str(n))
        features = []
        labels = []
        for media in glob.iglob(os.path.join(str(loadPath), "*.png")):
            (keypoints, descriptors) = self.__cachedetect(media, image_type)
            if (image_type == ImageType.HINT_NUMBER):
                #logger.info(keypoints)
                pass
            features.append(descriptors)
            if (image_type == ImageType.HINT_NUMBER):
                labels.append(n)
            else:
                labels.append(os.path.basename(media))
        classifier.fit(features, labels)
        logger.info('load classifier')
        logger.info(classifier.labels)
    @functools.lru_cache(maxsize=8)
    def __cachedetect(self, media, image_type=None):
        pro = DataProcessor(media, image_type)
        if pro.prepare() is None:
            logger.error('image error:{0}'.format(media))
            return None, None
        batch = pro.batch()
        if image_type == ImageType.RAW:
            cv2.imwrite('./base_color.png', pro.color)
            cv2.imwrite('./base_binary.png', batch)
        elif image_type == ImageType.NUMBER \
                or image_type == ImageType.HINT_NUMBER  \
                or image_type == ImageType.HINT_RAW:
            pass
        else:
            cv2.imwrite('./binary_{0}'.format(os.path.basename(media)), batch)
        return self.detector.detectAndCompute(batch, None)
    def getCountry(self, src):
        """
            @return country list
        """
        (keypoints, descriptors) = self.__cachedetect(src, ImageType.RAW)
        if keypoints is None:
            return None
        d = self.classifier.predict(descriptors)
        logger.info(d)
        #d2 = self.classifier.predict(descriptors, top_n=1)
        #logger.info(d2)
        return d
    def getNumber(self, src):
        (keypoints, descriptors) = self.__cachedetect(src, ImageType.NUMBER)
        if keypoints is None:
            return None
        d3 = self.numberclassifier.predict(descriptors, top_n=100)
        #logger.info(d3)
        return d3
    def classify(features):
        label = ''
        return label
    def createNumberData(self, media):
        """
            fillter
                1,頂点数が3未満
                2,面積が50未満
        """
        pro = DataProcessor(media, ImageType.PLAN)
        pro.prepare()
        batch = pro.batch()
        cv2.imwrite('./test/binary_color{0}'.format(os.path.basename(pro.name)), pro.color)
        cv2.imwrite('./test/binary_{0}'.format(os.path.basename(pro.name)), batch)
        image, contours, hierarchy = cv2.findContours(batch, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        rect=[]
        for c in contours:
            approx = cv2.approxPolyDP(c,1,True)
            if len(approx) < 3:
                continue
            area = cv2.contourArea(approx)
            if area < 50:
                continue
            
            cv2.drawContours(pro.color, [c], -1, (0,255,0), 3)
            rect.append(cv2.boundingRect(approx))
                

        rect = sorted(rect, key=lambda x:(x[1],x[0]))
        self.saveClipImage(pro, rect)
        return ''
    def saveClipImage(self, pro, rect):
        srcPath = Path(pro.name)
        srcfilename = os.path.basename(srcPath.stem)
        for i, value  in enumerate(rect):
            x, y = value[0], value[1]
            w, h = value[2], value[3]
            p1 = (x, y)
            p2 = (x+w, y+h)
            #cv2.rectangle(pro.color, p1, p2, 255, 2)
            roi = pro.color[y:y+h,x:x+w]
            #image = cv2.resize(pro.color[y:y+h,x:x+w],(32,32))
            image = roi
            cv2.imwrite('./test/{0}_{1}_{2}{3}'.format(srcfilename, i, value, srcPath.suffix), image)
    def classifyNumberImage(self):
        basepath = './test/'
        count = 0
        for media in glob.iglob(os.path.join(basepath, "*.png")):
            if  os.path.getsize(media) > 2048:
                continue
            count += 1
            d = self.getNumber(media)
            logger.info(d)
            s = sum([v for m,v in d.items()])
            if (s == 0):
                logger.warning('keypoint NotFound:{0}'.format(media))
                continue
            for k in d.keys():
                
                prefix = str(k)
                filename = os.path.join(basepath + prefix + '/', os.path.basename(media))
                directory = os.path.dirname(filename)
                if not os.path.exists(directory):
                    os.mkdir(directory)
                shutil.copy2(media, filename)
                break
        return None
    def getName(self, n):
        return self.names[n]

def main():
    config = configparser.ConfigParser()
    with open('./setting.ini', 'r', encoding='utf-8-sig') as f:
        config.read_file(f)
    c = country(config)
    # benchMark
    ele = ['./backup/hints/201702190825_0565e4fcbc166f00577cbd1f9a76f8c7.png',
        #    './backup/test/201702191909_ac08ccbbb04f2a1feeb4f8aaa08ae008.png',
        #     './backup/test/201702192006_2e268d7508c20aa00b22dfd41639d65e.png',
        ] * 2
    for l in ele:
        logger.info(l)
        for k in c.getCountry(l).keys():
            country_name = c.getName(k)
            logger.info(country_name)
            break;
    ele = ['./dat/number/sample/1.png',
           './dat/number/sample/1_1.png',
          ] * 1
    for l in ele:
        logger.info(l)
        d = c.getNumber(l)
    ele = ['./backup/hints/201702190825_0565e4fcbc166f00577cbd1f9a76f8c7.png',
           './backup/201702161156_919c7be6531ffeb5cfeb1e6e701556d3.png',
           './images/201702212104_4f1abbaf37872a27bec7f908a527f512.png',
          ] * 1
    for l in ele:
        c.createNumberData(l)    
    
    c.classifyNumberImage()
if __name__ == "__main__":
    main()