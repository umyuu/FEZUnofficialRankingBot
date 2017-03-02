# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
import configparser
import os
import tempfile
import glob
import functools

from pathlib import Path
# library
import cv2
# Myapp library
from classifier import Classifier
from ocrengine import OCREngine
from dataProcessor import DataProcessor, ImageType

logger = getLogger('myapp.tweetbot')
if __name__ == "__main__":
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)

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
            if image_type == ImageType.HINT_NUMBER:
                #logger.info(keypoints)
                pass
            features.append(descriptors)
            if image_type == ImageType.HINT_NUMBER:
                labels.append(n)
            else:
                labels.append(os.path.basename(media))
        classifier.fit(features, labels)
        #logger.info('load classifier')
        #logger.info(classifier.labels)
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
        
        pro = DataProcessor(src, ImageType.RAW)
        if pro.prepare() is None:
            logger.error('image error:{0}'.format(src))
            return None, None
        batch = pro.batch()
        baseName = Path(src)
        ocr = OCREngine()
        with tempfile.NamedTemporaryFile(delete=False, suffix=baseName.suffix) as temp:
             temp_file_name = temp.name
             logger.info(temp_file_name)
             cv2.imwrite(temp_file_name, batch)
        
        document = ocr.recognize(temp_file_name)
        for text in [document.rank1, document.rank2, document.rank3
                     , document.rank4, document.rank5]:
            logger.info('{name}/{score}'.format_map(text))

        #TextFormat()

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
            break
if __name__ == "__main__":
    main()
