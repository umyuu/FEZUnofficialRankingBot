# -*- coding: utf-8 -*-
import argparse
from abc import ABCMeta, abstractmethod
# library
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
    def addFilter(self, imagefilter):
        self.filters.append(imagefilter)
        return self
    def removeFilter(self, imagefilter):
        assert False, 'non implements'
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
            @params sender IImageFilter implemts class
        """
        pass

def main():
    parser = argparse.ArgumentParser(prog='hsvmask',
                                     description='HSV ColorMask Simulator')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.4')
    parser.add_argument('--image', '-in', default='../dat/Netzawar.png')
    args = parser.parse_args()
    print('args:{0}'.format(args))
    
    stream = ImageStream()
    stream.addFilter(GrayScaleFilter())
    stream.addFilter(AdaptiveThresholdFilter())
    stream.addFilter(IImageFilter())
    
    # 
    canvs = CanvesFillFilter()
    canvs.widthLimit = 400
    stream.addFilter(canvs)
 
    stream.data = cv2.imread(args.image)
    assert stream.data is not None
    cv2.imshow('image:', stream.data)
    cv2.waitKey(3000)
    # fillter処理
    stream.tofiltered()

if __name__ == "__main__":
    main()