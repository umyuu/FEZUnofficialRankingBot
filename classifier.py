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
        if (self.features is None):
            self.features = features
        self.features.extend(features)
        if (self.labels is None):
            self.labels = labels
        self.labels.extend(labels)
    def predict(self, descriptors, top_n=None):
        """
            @params descriptors image descriptors
                    top_n　　　　　　top n
            @return keys        label
                    value       sum(distance)
                    order by    value
        """
        d = dict()
        for i, value in enumerate(self.features):
            label = self.labels[i]
            try:
                dist = [m.distance for m in self.bf.match(descriptors, value)]
                #dist = [m.distance for m in self.bf.knnMatch(descriptors, self.features[k], 3)]
                #d[label] = sum(dist) / len(dist)
                l = len(dist)
                if (l == 0):
                    d[label] = sum(dist)
                else:
                    d[label] = sum(dist) / l
            except cv2.error:
                #d[label] = sys.maxsize
                d[label] = sys.minsize 
        
        sort = sorted(d.items(), key=lambda x: x[1])[:top_n]
        return OrderedDict(sort)
