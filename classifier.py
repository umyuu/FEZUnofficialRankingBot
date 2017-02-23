# -*- coding: utf-8 -*-
import os
import sys
from collections import OrderedDict
# library
import cv2

class Classifier(object):
    """
        note:implemets Classifier#match
             non implemets features detector
    """
    def __init__(self):
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    def fit(self, features):
        self.features = features
    def predict(self, descriptors):
        """
            @params descriptors image descriptors
            @return keys        basename
                    value       sum(distance)
                    order by    value
        """
        d = dict()
        for k in self.features.keys():
            basename = os.path.basename(k)
            try:
                dist = [m.distance for m in self.bf.match(descriptors, self.features[k])]
                #dist = [m.distance for m in self.bf.knnMatch(descriptors, self.features[k], 3)]
                d[basename] = sum(dist) / len(dist)
            except cv2.error:
                d[basename] = sys.maxsize

        return OrderedDict(sorted(d.items(), key=lambda x: x[1]))
