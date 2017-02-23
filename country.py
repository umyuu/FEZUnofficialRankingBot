# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
import configparser
import os
import sys
import glob
from collections import OrderedDict
import functools
# library
import cv2
# Myapp library
from hsvcolor import HSVcolor

logger = getLogger('myapp.tweetbot')
if __name__ == "__main__":
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)
class Classifier(object):
    def __init__(self, config):
        self.hints = config['WORK_FOLDER']['HINTS']
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        self.detector = cv2.AKAZE_create()
        pass
    #def fit(self, features, labels):
    #    return None
    def predict(self, first):
        """
            @return keys        basename
                    value       sum(distance)
                    order by    value
        """
        (kp_first, des_first) = self.detector.detectAndCompute(first, None)
        d = dict()
        for media in glob.iglob(os.path.join(self.hints, "*.png")):
            basename = os.path.basename(media)
            try:
                (kp_second, des_second) = self.__cachedetect(media)
                dist = [m.distance for m in self.bf.match(des_first, des_second)]
                #dist = [m.distance for m in self.bf.knnMatch(des_first, des_second, 3)]
                d[basename] = sum(dist) / len(dist)
            except cv2.error:
                d[basename] = sys.maxsize

        return OrderedDict(sorted(d.items(), key=lambda x: x[1]))
    @functools.lru_cache(maxsize=8)
    def __cachedetect(self, media):
        pro = DataProcessor(media)
        if pro.prepare() is None:
           return None
        cv2.imwrite('./binary_{0}'.format(os.path.basename(media)), pro.batch())
        return self.detector.detectAndCompute(pro.batch(), None)
class DataProcessor(object):
    def __init__(self, name):
        self.__name = name
        self.color = None
        self.hsv = None
        # todo:static fileds
        self.__contryMask = {'netzawar':(HSVcolor(175, 55, 0), HSVcolor(255, 255, 255)),
                             'casedria':(HSVcolor(53, 0, 0), HSVcolor(79, 255, 255)),
                             'geburand':(HSVcolor(120, 0, 100), HSVcolor(150, 255, 255)), 
                             'hordine':(HSVcolor(24, 0, 249), HSVcolor(30, 255, 255)),
                             'ielsord':(HSVcolor(79, 0, 0), HSVcolor(112, 255, 255))}
    @property
    def name(self):
        return self.__name
    def prepare(self):
        """
            @return color image
        """
        zoom = 2
        c = cv2.imread(self.name)
        if c is None:
            logger.info("notfound:{0}".format(self.name))
            return c
        self.color = cv2.resize(c, (c.shape[1]*zoom, c.shape[0]*zoom), interpolation=cv2.INTER_CUBIC)
        if self.color is not None:
            self.hsv = cv2.cvtColor(self.color, cv2.COLOR_BGR2HSV)
        else:
            self.hsv = None        
        return self.color
    def batch(self,ranking=None):
        """
            masking)
                step1:white color
                step2:color -> grayscale -> adaptiveThreshold -> binary
                step3:country color
                step4:fill min(500, height)
            @return binary image
        """
        white = self.__getWhiteMasking(self.hsv)
        binary = self.__binary_threshold(self.color)
        # white color
        binary = cv2.bitwise_and(binary, binary, mask=white)
        #fez country color mask pattern
        lower, upper = self.__contryMask['netzawar']
        binary = cv2.bitwise_not(binary, binary, mask=self.__inRange(self.hsv, lower, upper))
        lower, upper = self.__contryMask['geburand']
        binary = cv2.bitwise_not(binary, binary, mask=self.__inRange(self.hsv, lower, upper))
        lower, upper = self.__contryMask['ielsord']
        binary = cv2.bitwise_not(binary, binary, mask=self.__inRange(self.hsv, lower, upper))
        lower, upper = self.__contryMask['casedria']
        binary = cv2.bitwise_not(binary, binary, mask=self.__inRange(self.hsv, lower, upper))
        lower, upper = self.__contryMask['hordine']
        binary = cv2.bitwise_not(binary, binary, mask=self.__inRange(self.hsv, lower, upper))
        
        # １位より下を黒色で塗りつぶしてマスク。
        height, width = self.color.shape[:2]
        cv2.rectangle(binary, (0, min(500, height)), (width,height), (0,0,0), -1)
        return binary
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
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        self.detector = cv2.AKAZE_create()
        self.classifier = Classifier(config)
    def __Detection(self, first):
        """
            @return keys        basename
                    value       sum(distance)
                    order by    value
        """
        (kp_first, des_first) = self.detector.detectAndCompute(first, None)
        d = dict()
        for media in glob.iglob(os.path.join(self.hints, "*.png")):
            basename = os.path.basename(media)
            try:
                (kp_second, des_second) = self.__cachedetect(media)
                dist = [m.distance for m in self.bf.match(des_first, des_second)]
                #dist = [m.distance for m in self.bf.knnMatch(des_first, des_second, 3)]
                d[basename] = sum(dist) / len(dist)
            except cv2.error:
                d[basename] = sys.maxsize

        return OrderedDict(sorted(d.items(), key=lambda x: x[1]))
    @functools.lru_cache(maxsize=8)
    def __cachedetect(self, media):
        pro = DataProcessor(media)
        if pro.prepare() is None:
           return None
        cv2.imwrite('./binary_{0}'.format(os.path.basename(media)), pro.batch())
        return self.detector.detectAndCompute(pro.batch(), None)
    def getCountry(self, src):
        """
            @return country list
        """
        pro = DataProcessor(src)
        if pro.prepare() is None:
           logger.error('image error:{0}'.format(src))
           return None
        binary = pro.batch(1)
        # imwrite#cvtColorで色情報が足りないとエラー
        cv2.imwrite('./base_color.png', pro.color)
        cv2.imwrite('./base_binary.png', binary)
        

        
        d1 = self.classifier.predict(binary)
        
        d = self.__Detection(binary)
        logger.info(d1)
        logger.info(d)
        
        return d
    def getName(self, n):
        return self.names[n]

def main():
    config = configparser.ConfigParser()
    with open('./setting.ini', 'r', encoding='utf-8-sig') as f:
        config.read_file(f)
    c = country(config)
    # benchMark
    for i in range(1):
        ele = ['./backup/hints/201702190825_0565e4fcbc166f00577cbd1f9a76f8c7.png',
        #     './backup/test/201702191909_ac08ccbbb04f2a1feeb4f8aaa08ae008.png',
        #     './backup/test/201702192006_2e268d7508c20aa00b22dfd41639d65e.png',
             ]
        for l in ele:
            logger.info(l)
            d = c.getCountry(l)
            for k in d.keys():
                country_name = c.getName(k)
                logger.info(country_name)
                break;
        
if __name__ == "__main__":
    main()