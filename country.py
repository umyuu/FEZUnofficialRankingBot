# -*- coding: utf-8 -*-
from logging import getLogger
import configparser
import os
import sys
import glob
from collections import OrderedDict
import cv2
import numpy as np
logger = getLogger('myapp.tweetbot')

class DataProcessor():
    def __init__(self, name):
        self._name = name
        self.color = None
    def prepare(self):
        self.color = self.__read(self._name)
        if self.color is None:
            return None
        return self.color
    def batch(self):
        # 画像の白文字部分を抽出
        white = self.__getWhiteMasking(self.color.copy())
        binary = self.__binary_threshold(self.color)
        # マスク
        binary = cv2.bitwise_and(binary, binary, mask= white)
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
    def __resize(self, img, zoom=2):
        return cv2.resize(img, (img.shape[1]*zoom, img.shape[0]*zoom), interpolation=cv2.INTER_CUBIC)
    def __binary_threshold(self, img):
        greyscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(greyscale, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
            cv2.THRESH_BINARY, 11, 2)
        return thresh
    def __read(self, name, zoom=2):
        color = cv2.imread(name)
        if color is None:
            print("notfound:{0}".format(name))
            return None
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
        (kp_first, des_first) = self.detector.detectAndCompute(first, None)
        d = dict()
        for media in glob.iglob(os.path.join(self.hints, "*.png")):
            basename = os.path.basename(media)
            try:
                pro = DataProcessor(media)
                if pro.prepare() is None:
                    return
                second = pro.batch()
                (kp_second, des_second) = self.detector.detectAndCompute(second, None)
                dist = [m.distance for m in self.bf.match(des_first, des_second)]
                result = sum(dist) / len(dist)
                d[basename] = result
            except cv2.error:
                d[basename] = sys.maxsize

        return OrderedDict(sorted(d.items(), key=lambda x: x[1]))
    def getCountry(self, src):
        pro = DataProcessor(src)
        if pro.prepare() is None:
           return
        binary = pro.batch()
        # imwrite#cvtColorで色情報が足りないとエラー
        cv2.imwrite('./b_color.png', pro.color)
        cv2.imwrite('./b_binary.png', binary)
        d = self.__Detection(binary)
        print(d)
        return d
    def getName(self, n):
        return self.names[n]

def main():
    config = configparser.ConfigParser()
    with open('./setting.ini', 'r', encoding='utf-8-sig') as f:
        config.read_file(f)
    c = country(config)
    #d = c.getCountry('./backup/hints/Hordine.png')
    for i in range(3):
        d = c.getCountry('./backup/hints/201702190825_0565e4fcbc166f00577cbd1f9a76f8c7.png')
        for k in d.keys():
            country_name = c.getName(k)
            print(country_name)
            break;
    
if __name__ == "__main__":
    main()