# -*- coding: utf-8 -*-
import argparse
# library
import cv2

class ImageStream(object):
    def __init__(self, preprocessor=None, task=None, finish=None):
        if preprocessor is None:
            preprocessor = self.Empty
        if task is None:
            task = self.Empty
        if finish is None:
            finish = self.Empty
        self.preprocessor = preprocessor
        self.task = task
        self.finish = finish
    def Empty(self, stream):
        """
            stream => result
            @param {stream}  stream
            @return {stream} stream
        """
        return stream
    def transform(self, data):
        for t in [self.preprocessor, self.task, self.finish]:
            data = t(data)
            cv2.imshow('image:', data)
            cv2.waitKey(3000)
        return data
class Processor(object):
    def prepare(self, stream):
        assert stream is not None
        return stream
    def task(self, stream):
        """
            filtered prepare
            @param {image}  stream
            @return {image} filtered
        """
        result = stream
        result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        result = cv2.adaptiveThreshold(result
                    , 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 3)
        return result
    def finish(self, stream):
        height, width = stream.shape[:2]
        widthLimit = 400
        cv2.rectangle(stream, (0, min(widthLimit, height)), (width, height), (0 , 0, 0), -1)
        return stream
def main():
    parser = argparse.ArgumentParser(prog='ImageFilter',
                                     description='ImageFilter Simulator')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument('--image', '-in', default='../resource/Netzawar.png')
    args = parser.parse_args()
    print('args:{0}'.format(args))
    
    p = Processor()
    stream = ImageStream(preprocessor=p.prepare, task=p.task, finish=p.finish)
    data = cv2.imread(args.image)
    #
    stream.transform(data)

if __name__ == "__main__":
    main()