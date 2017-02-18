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
    def drawContours(self, color, src):
        _, contours, _ = cv2.findContours(src, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            #if cv2.contourArea(c) < 90:
            #    continue
            approx = None
            #cv2.convexHull(c, approx);
            epsilon = 0.01 * cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, epsilon, True)
            #s=abs(cv2.contourArea(c))
            #if s <= AREA_MAX:
            #if len(approx) == 4:
            #cv2.drawContours(color, c, -1, (0, 0, 255), 3)
            #cv2.drawContours(color, [approx], -1, (0, 255, 0), 3)
            x,y,w,h = cv2.boundingRect(c)
            color = cv2.rectangle(color,(x,y),(x+w,y+h),(0,255,0),2)
            
            
            #approx = cv2.convexHull(c)
            #rect = cv2.boundingRect(approx)
            #cvRectangle
        #plt.imshow(color)
        #contours, _ = cv2.findContours(src, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #rects = []
        #for contour in contours:
        #    approx = cv2.convexHull(contour)
        #    rect = cv2.boundingRect(approx)
        #    rects.append(np.array(rect))

        #plt.imshow(cv2.cvtColor(color, cv2.COLOR_BGR2RGB))
        #plt.show()

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
    def read(self, name):
        print("read")
        color = cv2.imread(name)
        if color is None:
            print("notfound")
            return None
        # resize
        zoom=2
        return cv2.resize(color, (color.shape[1]*zoom, color.shape[0]*zoom), interpolation=cv2.INTER_CUBIC)
        template = cv2.imread('./hints/template.png')
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
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
        inv = cv2.bitwise_not(binary)
        #self.drawContours(color, inv)
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # 
        #

        #
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