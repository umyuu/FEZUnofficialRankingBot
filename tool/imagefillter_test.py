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
class IregalClassFilter(object):
    def __init__(self):
        pass
class ImageStream(object):
    __slots__ = ['filters','data']
    def __init__(self):
        self.filters = []
        self.data = None
    def addFilter(self, f):
        if not isinstance(f, IImageFilter):
            assert False, 'non implements'
        if not (f in self.filters):
            self.filters.append(f)
        return self
    def removeFilter(self, f):
        if not isinstance(f, IImageFilter):
            assert False, 'non implements'
        if f in self.filters:
            self.filters.remove(f)
        return self
    def clearFilter(self):
        self.filters = []
        return self
    def tofiltered(self):
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
        print(sender.name + ':event')
        cv2.imshow('image:', self.data)
        cv2.waitKey(3000)
        pass
def test_scenario1():
    stream = ImageStream()
    stream.addFilter(IregalClassFilter())
def test_scenario2():
    stream = ImageStream()
    empty = EmptyFilter()
    stream.addFilter(empty)
    stream.addFilter(empty)
def main():
    parser = argparse.ArgumentParser(prog='ImageFilter',
                                     description='ImageFilter Simulator')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument('--image', '-in', default='../dat/Netzawar.png')
    args = parser.parse_args()
    print('args:{0}'.format(args))
    
    stream = ImageStream()
    stream.addFilter(EmptyFilter())
    stream.addFilter(GrayScaleFilter())
    stream.addFilter(AdaptiveThresholdFilter())
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