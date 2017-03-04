# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
#
import cv2

class IImageFilter(metaclass=ABCMeta):
    def __init__(self, name='IImageFilter'):
        self.name = name
    @abstractmethod
    def filtered(self, stream):
        """
            @params stream source stream
            @return filtered stream
        """
        return stream
class EmptyFilter(IImageFilter):
    def __init__(self):
        super().__init__('EmptyFilter')
    def filtered(self, stream):
        return stream
class GrayScaleFilter(IImageFilter):
    def __init__(self):
        super().__init__('GrayScaleFilter')
    def filtered(self, stream):
        result = cv2.cvtColor(stream, cv2.COLOR_BGR2GRAY)
        return result

class AdaptiveThresholdFilter(IImageFilter):
    def __init__(self):
        super().__init__('AdaptiveThresholdFilter')
    def filtered(self, stream):
        result = cv2.adaptiveThreshold(stream
                    , 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 3)
        return result

class CanvesFillFilter(IImageFilter):
    def __init__(self):
        super().__init__('CanvesFillFilter')
    def filtered(self, stream):
        height, width = stream.shape[:2]
        cv2.rectangle(stream, (0, min(self.widthLimit, height)), (width,height), (0,0,0), -1)
        return stream

class ImageStream(object):
    __slots__ = ['filters','data']
    def __init__(self):
        self.filters = []
        self.data = None
    def addFilter(self, f):
        if not isinstance(f, IImageFilter):
            assert False, 'NotImplemented'
        if not (f in self.filters):
            self.filters.append(f)
        return self
    def removeFilter(self, f):
        if not isinstance(f, IImageFilter):
            assert False, 'NotImplemented'
        if f in self.filters:
            self.filters.remove(f)
        return self
    def clearFilter(self):
        self.filters = []
        return self
    def tofiltered(self):
        """
            @return filtered stream
        """
        for f in self.filters:
            self.data = f.filtered(self.data)
            assert self.data is not None, 'filtered result None'
            self.fire_onfiltered(f)
        return self.data
    def fire_onfiltered(self, sender):
        """
            filtered event
            @params sender IImageFilter implemts class
        """
        pass
