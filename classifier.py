# -*- coding: utf-8 -*-
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
        self.features = None
        self.labels = None
    def fit(self, features, labels):
        """
            @params features descriptors[]
                    labels target label[]
        """
        self.features = features
        self.labels = labels
    def predict(self, descriptors, top_n=None):
        """
            @params descriptors image descriptors
                    top_n　　　　　　top n
            @return keys        label
                    value       sum(distance)
                    order by    value
        """
        d = dict()
        for k in self.features.keys():
            label = self.labels[k]
            try:
                dist = [m.distance for m in self.bf.match(descriptors, self.features[k])]
                #dist = [m.distance for m in self.bf.knnMatch(descriptors, self.features[k], 3)]
                d[label] = sum(dist) / len(dist)
            except cv2.error:
                #d[label] = sys.maxsize
                d[label] = sys.minsize 
        
        sort = sorted(d.items(), key=lambda x: x[1])[:top_n]
        return OrderedDict(sort)
