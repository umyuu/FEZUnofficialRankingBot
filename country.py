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
import numpy as np
logger = getLogger('myapp.tweetbot')
if __name__ == "__main__":
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)

class DataProcessor():
    def __init__(self, name):
        self._name = name
        self.color = None
    def prepare(self):
        """
            @return color image
        """
        self.color = self.__read(self._name)
        if self.color is None:
            return None
        return self.color
    def batch(self,ranking=1):
        """
            @return binary image
        """
        # 画像の白文字部分を抽出
        white = self.__getWhiteMasking(self.color.copy())
        binary = self.__binary_threshold(self.color)
        # マスク
        binary = cv2.bitwise_and(binary, binary, mask=white)
        # １位より下を黒色で塗りつぶしてマスク。
        height, width = self.color.shape[:2]
        cv2.rectangle(binary, (0, min(500, height)), (width,height), (0,0,0), -1)
        return binary
    def __getWhiteMasking(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        sensitivity = 15
        lower_white = np.array([0, 0, 255 - sensitivity])
        upper_white = np.array([255, sensitivity, 255])
        return cv2.inRange(hsv, lower_white, upper_white)
    def __getRedMasking(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_Red = np.array([106, 47, 71])
        upper_Red = np.array([106, 47, 71])
        return cv2.inRange(hsv, lower_Red, upper_Red)
    def __binary_threshold(self, img):
        greyscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(greyscale, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
            cv2.THRESH_BINARY, 11, 2)
        return thresh
    def __read(self, name, zoom=2):
        color = cv2.imread(name)
        if color is None:
            logger.info("notfound:{0}".format(name))
            return None
        # note:cv2.resize remove must #batch change
        return cv2.resize(color, (color.shape[1]*zoom, color.shape[0]*zoom), interpolation=cv2.INTER_CUBIC)
class country():
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
        #cv2.imwrite('./binary_{0}.png'.format(os.path.basename(media)), pro.batch())
        return self.detector.detectAndCompute(pro.batch(), None)
    def getCountry(self, src):
        """
            @return country list
        """
        pro = DataProcessor(src)
        if pro.prepare() is None:
           logger.error('image error:{0}'.format(src))
           return None
        binary = pro.batch()
        # imwrite#cvtColorで色情報が足りないとエラー
        #cv2.imwrite('./b_color.png', pro.color)
        #cv2.imwrite('./b_binary.png', binary)
        d = self.__Detection(binary)
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
             './backup/test/201702191909_ac08ccbbb04f2a1feeb4f8aaa08ae008.png',
             './backup/test/201702192006_2e268d7508c20aa00b22dfd41639d65e.png',
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