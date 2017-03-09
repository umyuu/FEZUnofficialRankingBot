# -*- coding: utf-8 -*-
import argparse
# library
import cv2
# pylint: disable=C0103

class ImageStream(object):
    """
        ImageStream stream transform
    """
    def __init__(self, preprocessor=None, task=None, finish=None):
        self.filters = []
        if preprocessor is None:
            preprocessor = self.EmptyFilter
        if task is None:
            task = self.EmptyFilter
        if finish is None:
            finish = self.EmptyFilter
        self.filters.append(preprocessor)
        self.filters.append(task)
        self.filters.append(finish)
    def EmptyFilter(self, sender, args):
        """
            EmptyFilter
               stream => result
            usage ImageStream(task=ImageStream().EmptyFilter)
            @param {object}sender
                   {object},{None}args event args
            @return {object}
        """
        return sender
    def transform(self, data, args=None):
        """
            call
                preprocessor => task => finish
            @param {dict}data stream & param
            @return {dict}
        """
        for caller in self.filters:
            data = caller(data, args)
            cv2.imshow('image:', data)
            cv2.waitKey(3000)
        return data
class Processor(object):
    """
        ImageStream caller Processor method.
    """
    def prepare(self, sender, ev):
        """
            filtered prepare
            @param {dict}sender  stream & param
        """
        result = sender
        assert result is not None
        return result
    def task(self, sender, ev):
        """
            filtered task
            @param {dict}sender  stream & param
        """
        result = cv2.cvtColor(sender, cv2.COLOR_BGR2GRAY)
        result = cv2.adaptiveThreshold(result
                    , 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 3)
        return result
    def finish(self, sender, ev):
        """
            filtered finish
            @param {dict}sender    stream & param
        """
        result = sender
        height, width = result.shape[:2]
        widthLimit = 400
        cv2.rectangle(result, (0, min(widthLimit, height)), (width, height), (0, 0, 0), -1)
        return result
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
