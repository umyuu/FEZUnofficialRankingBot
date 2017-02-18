# -*- coding: utf-8 -*-
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
    def FeatureDetection(self):
        img = cv2.imread('img.jpg')
        detector = cv2.ORB_create()
        keypoints = detector.detect(img)
        out = cv2.drawKeypoints(img, keypoints, None)
        cv2.imshow("keypoints", out)
        

    def drawContours(self, src):
        #imgray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        
        imgray = src
        #imgray = cv2.resize(imgray, (imgray.shape[1]*2, imgray.shape[0]*2), interpolation=cv2.INTER_CUBIC)
        imgray = cv2.Laplacian(imgray, cv2.CV_32F,ksize=3)
        cv2.imwrite('./hints/aaaacccc.png', imgray)
        #ret,thresh = cv2.threshold(imgray, 127, 255, 0)
        thresh = cv2.Canny(imgray, threshold1=90, threshold2=110)
        cv2.imwrite('./hints/aaaa.png', thresh)
        #image, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #img = cv2.drawContours(src, contours, -1, (0,255,0), 3)
        #cv2.imwrite('./hints/aaaa.png', img)
    def drawEgge(self, cups_preprocessed):
        cups_edges = cv2.Canny(cups_preprocessed, threshold1=90, threshold2=110)
        plt.imshow(cv2.cvtColor(cups_edges, cv2.COLOR_GRAY2RGB))
        cv2.imwrite('cups-edges.jpg', cups_edges)
    def getWhiteMasking(self, img):
        
        # 取得する色の範囲を指定する
        sensitivity = 16
        lower_white = np.array([0, 0, 255 - sensitivity])
        upper_white = np.array([255, sensitivity, 255])
        return cv2.inRange(img, lower_white, upper_white)
        #res = cv2.bitwise_and(img, img, mask= img_mask)
        #cv2.imwrite('./hints/cccc.png', res) 
    def getRect(self,l_img):
        

        # 白枠で縁取られた面積最大の領域を探す
        image, contours, hierarchy = cv2.findContours(l_img,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)

        inner_contours = []
        for index, contour in enumerate(contours):
            if hierarchy[0][index][2] == -1:
                inner_contours.append(contour)

        approxes = []
        max_box = None
        for contour in inner_contours:
            # 矩形補完
            epsilon = 0.01*cv2.arcLength(contour,True)
            approx = cv2.approxPolyDP(contour,epsilon,True)
            area = cv2.contourArea(approx)

            if max_box is None or cv2.contourArea(max_box) < cv2.contourArea(approx):
                max_box = approx
                if(area > 20):
                    approxes.append(approx)
            x,y,w,h = cv2.boundingRect(contour)
            l_img = cv2.rectangle(l_img,(x,y),(x+w,y+h),(0,255,0),2)
            
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
    def aaaa(self):
        print('aaaa')
        #im_mask = cv2.imread('./hints/white.png')
        img = cv2.imread('./hints/netzawar.png')
        if img is None:
            print("notfound")
            return
        # 画像の白文字部分を抽出
        img = self.resize(img)
        #img = self.binary_threshold(img)
        #img = cv2.bitwise_not(img)
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # 
        #

        #
        img = self.getWhiteMasking(img)

        aaaa = image()
        aaaa._image = img
        aaaa.save('./hints/fffff.png')
        
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