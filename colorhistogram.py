# -*- coding: utf-8 -*-
import os
import glob
import cv2
import numpy as np
import matplotlib.pyplot as plt
class image():
    def __init__(self):
        self._image = None
    def save(self, name):
        # cvtColorで色情報が足りないとエラー
        #img = cv2.cvtColor(self._image, cv2.COLOR_HSV2BGR)
        cv2.imwrite(name, self._image)
class colorhistogram():
    def colorHist(self, img):
        color = ('b','g','r')
        for i,col in enumerate(color):
            histr = cv2.calcHist([img],[i],None,[256],[0,256])
            plt.plot(histr,color = col)
            plt.xlim([0,256])
        plt.show()
    def Knn(self):
        np.random.seed(42)
        # Feature set containing (x,y) values of 25 known/training data
        trainData = np.random.randint(0,100,(25,2)).astype(np.float32)

        # Labels each one either Red or Blue with numbers 0 and 1
        responses = np.random.randint(0,2,(25,1)).astype(np.float32)

        # Take Red families and plot them
        red = trainData[responses.ravel()==0]
        plt.scatter(red[:,0],red[:,1],80,'r','^')

        # Take Blue families and plot them
        blue = trainData[responses.ravel()==1]
        plt.scatter(blue[:,0],blue[:,1],80,'b','s')

        plt.show()
        newcomer = np.random.randint(0,100,(1,2)).astype(np.float32)
        plt.scatter(newcomer[:,0],newcomer[:,1],80,'g','o')

        knn = cv2.ml.KNearest_create()
        knn.train(trainData, responses)
        ret, results, neighbours ,dist = knn.find_nearest(newcomer, 3)

        print ("result: ", results,"\n")
        print ("neighbours: ", neighbours,"\n")
        print ("distance: ", dist)

        plt.show()
    def FeatureDetection(self, target_img):
        bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        detector = cv2.AKAZE_create()
        (target_kp, target_des) = detector.detectAndCompute(target_img, None)
        ser = []
        for media in glob.iglob(os.path.join('./hints/sample/', "*.png")):
            comparing_img_path = media
            try:
                
                comparing_img = self.read(comparing_img_path)
                white = self.getWhiteMasking(comparing_img.copy())
                comparing_img = self.binary_threshold(comparing_img)
                comparing_img = cv2.bitwise_and(comparing_img, comparing_img, mask= white)
                (comparing_kp, comparing_des) = detector.detectAndCompute(comparing_img, None)
                dist = [m.distance for m in bf.match(target_des, comparing_des)]
                ret = sum(dist) / len(dist)
            except cv2.error:
                ret = 100000
            print(media, ret)
        return ser
    def getWhiteMasking(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        sensitivity = 15
        lower_white = np.array([0, 0, 255 - sensitivity])
        upper_white = np.array([255, sensitivity, 255])
        return cv2.inRange(hsv, lower_white, upper_white)
    def getRedMasking(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([106, 47, 71])
        upper_blue = np.array([106, 47, 71])
        return cv2.inRange(hsv, lower_blue, upper_blue)
        #res = cv2.bitwise_and(img, img, mask= img_mask)
        #cv2.imwrite('./hints/cccc.png', res) 
    def calcHist(self, img):
        #self.colorHist(img)
        #self.Knn()
        im_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        #hist = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
        print("calcHist")
        h_h = cv2.calcHist([im_hsv], [0], None, [180], [0, 180], None, 0)
        h_s = cv2.calcHist([im_hsv], [1], None, [256], [0, 256], None, 0)
        h_v = cv2.calcHist([im_hsv], [2], None, [256], [0, 256], None, 0)
        #h_h = cv2.calcHist([im_hsv], [0], im_mask, [180], [0, 180], None, 0)
        #h_s = cv2.calcHist([im_hsv], [1], im_mask, [256], [0, 256], None, 0)
        #h_v = cv2.calcHist([im_hsv], [2], im_mask, [256], [0, 256], None, 0)
        print("end calcHist")
        #plt.imshow(hist,interpolation = 'nearest')
        #plt.imshow(hist,interpolation = 'nearest')
        #color = ('b','g','r')
        for h in [h_h, h_s, h_v]:
            plt.imshow(h,interpolation = 'nearest')
            #plt.imshow(h)
            #plt.plot(h,color = col)
            #plt.xlim([0,256])
        #plt.show()
                #cv2.imshow('im',im)
        
        #plt.imshow(hist,interpolation = 'nearest')
        #h_dist = cv2.compareHist(face_hist[0], hists[0], 1)
    def resize(self, img, zoom=2):
        return cv2.resize(img, (img.shape[1]*zoom, img.shape[0]*zoom), interpolation=cv2.INTER_CUBIC)
    def binary_threshold(self, img):
        greyscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(greyscale, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
            cv2.THRESH_BINARY, 11, 2)
        return thresh
    def read(self, name):
        #print("read")
        color = cv2.imread(name)
        if color is None:
            print("notfound")
            return None
        # resize
        zoom=2
        return cv2.resize(color, (color.shape[1]*zoom, color.shape[0]*zoom), interpolation=cv2.INTER_CUBIC)
    def matchTemplate(self, src):
        template = cv2.imread('./hints/template.png')
        template = self.binary_threshold(template)
        if len(template.shape) == 3:
            height, width, channels = template.shape[:3]
        else:
            height, width = template.shape[:2]
            channels = 1
        template_width = width
        template_height = height
        matches = cv2.matchTemplate(src, template, cv2.TM_CCORR_NORMED)

        mn,_,mnLoc,_ = cv2.minMaxLoc(matches)
        x, y = mnLoc
        print(mn)
        print(mnLoc)
        margin_with = 5
        threshold = 0.73
        src = cv2.rectangle(src, (x, y),
                        (x + template_width + margin_with, y + template_height),
                         (0, 0, 255), 2)
                    
        cv2.imshow('score', src)       
        cv2.waitKey(0)
        
        clip = src[y:y + height, x:x + width]
        #sss =src[x:y, (x + template_width + margin_with): (y + template_height)]
        cv2.imshow('score', clip)
        cv2.waitKey(0)
        return clip
    def aaaa(self):
        color = self.read('./hints/netzawar.png')
        if color is None:
            return
        white = self.getWhiteMasking(color.copy())
        red = self.getRedMasking(color.copy())
        # 画像の白文字部分を抽出
        #resized = self.resize(color)
        binary = self.binary_threshold(color)
        binary = cv2.bitwise_and(binary, binary, mask= white)
        
        
        # 白黒反転
        #inv = cv2.bitwise_not(binary)
        #self.drawContours(color, inv)
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # 
        #

        #
        self.FeatureDetection(binary)
        #self.matchTemplate(inv)
        
        
        aaaa = image()
        aaaa._image = inv
        aaaa.save('./hints/fffff.png')
        aaaa._image = color
        aaaa.save('./hints/color.png')

        #img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        
        #cv2.imwrite('./hints/bbbb.png', img)

        
        #res = self.getWhiteMaskImage(img)
        #self.drawContours(img)
        
        #self.getRect(res)
        #cv2.imwrite('./hints/dddd.png', res)
        #res = self.drawContours(res)
       
def main():
    c = colorhistogram()
    c.aaaa()
    
if __name__ == "__main__":
    main()