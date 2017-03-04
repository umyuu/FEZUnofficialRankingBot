# -*- coding: utf-8 -*-
#
import os
import cv2
from pathlib import Path
#
from dataprocessor import DataProcessor, ImageType

class Clipping(object):
    def __init__(self, media, target=None):
        self.media = media
        self.target = target
        pro = DataProcessor(self.media, ImageType.PLAN)
        pro.prepare()
        self.binary = pro.batch()
        self.color = pro.color
        self.drawClipSource = True
    def number(self):
        """
            fillter
                1,頂点数が3未満
                2,面積が50未満
        """
        cv2.imwrite('./test/binary_color{0}'.format(os.path.basename(self.media)), self.color)
        cv2.imwrite('./test/binary_{0}'.format(os.path.basename(self.media)), self.binary)
        image, contours, hierarchy = cv2.findContours(self.binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        rect = []
        for c in contours:
            approx = cv2.approxPolyDP(c,1,True)
            if len(approx) < 3:
                continue
            area = cv2.contourArea(approx)
            if area < 50:
                continue
            if self.drawClipSource:
                cv2.drawContours(self.color, [c], -1, (0,255,0), 3)
                pass
            rect.append(cv2.boundingRect(approx))

        rect = sorted(rect, key=lambda x:(x[1], x[0]))
        self.splitImage(rect)
        return ''
    def splitImage(self, rect):
        srcPath = Path(self.media)
        srcfilename = os.path.basename(srcPath.stem)
        for i, value  in enumerate(rect):
            x, y = value[0], value[1]
            w, h = value[2], value[3]
            p1 = (x, y)
            p2 = (x+w, y+h)
            cv2.rectangle(self.color, p1, p2, (0,255,0), 2)
            roi = self.color[y:y+h,x:x+w]
            #roi = roi.shape[:2]
            #image = cv2.resize(self.color[y:y+h,x:x+w],(32,32))
            image = roi
            cv2.imwrite('./test/{0}_{1}_{2}{3}'.format(srcfilename, i, value, srcPath.suffix), image)