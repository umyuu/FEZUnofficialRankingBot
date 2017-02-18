# -*- coding: utf-8 -*-
import os
import sys
import glob
import cv2
import numpy as np
class image():
    def __init__(self):
        self._image = None
    def save(self, name):
        # cvtColorで色情報が足りないとエラー
        #img = cv2.cvtColor(self._image, cv2.COLOR_HSV2BGR)
        cv2.imwrite(name, self._image)
class country():
    def __init__(self):
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        self.detector = cv2.AKAZE_create()
    def Detection(self, first):
        (kp_first, des_first) = self.detector.detectAndCompute(first, None)
        d = dict()
        for media in glob.iglob(os.path.join('./hints/sample/', "*.png")):
            try:
                second = self.read(media)
                white = self.getWhiteMasking(second.copy())
                second = self.binary_threshold(second)
                second = cv2.bitwise_and(second, second, mask= white)
                (kp_second, des_second) = self.detector.detectAndCompute(second, None)
                dist = [m.distance for m in self.bf.match(des_first, des_second)]
                result = sum(dist) / len(dist)
                d[media] = result
            except cv2.error:
                d[media] = sys.maxsize

        return sorted(d.items(), key=lambda x: x[1])
    def getWhiteMasking(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        sensitivity = 15
        lower_white = np.array([0, 0, 255 - sensitivity])
        upper_white = np.array([255, sensitivity, 255])
        return cv2.inRange(hsv, lower_white, upper_white)
    def getRedMasking(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_Red = np.array([106, 47, 71])
        upper_Red = np.array([106, 47, 71])
        return cv2.inRange(hsv, lower_Red, upper_Red)
    def resize(self, img, zoom=2):
        return cv2.resize(img, (img.shape[1]*zoom, img.shape[0]*zoom), interpolation=cv2.INTER_CUBIC)
    def binary_threshold(self, img):
        greyscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(greyscale, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
            cv2.THRESH_BINARY, 11, 2)
        return thresh
    def read(self, name,zoom=2):
        #print("read")
        color = cv2.imread(name)
        if color is None:
            print("notfound")
            return None
        # resize
        return cv2.resize(color, (color.shape[1]*zoom, color.shape[0]*zoom), interpolation=cv2.INTER_CUBIC)
    def getcountry(self, src):
        color = self.read(src)
        if color is None:
            return
        # 画像の白文字部分を抽出
        white = self.getWhiteMasking(color.copy())
        binary = self.binary_threshold(color)
        # マスク
        binary = cv2.bitwise_and(binary, binary, mask= white)
        # 画像から国名を抽出
        #aaaa = image()
        #aaaa._image = binary
        #aaaa.save('./hints/fffff.png')
        #aaaa._image = color
        #aaaa.save('./hints/color.png')
        return self.Detection(binary)

def main():
    c = country()
    c.getcountry('./hints/hordaine.png')

if __name__ == "__main__":
    main()