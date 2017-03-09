# -*- coding: utf-8 -*-
from logging import getLogger
from enum import Enum, unique
from pathlib import Path
from io import BytesIO
#
import cv2
import numpy as np
#
from serializer import Serializer
from hsvcolor import HSVcolor
from iimagefillter import GrayScaleFilter, AdaptiveThresholdFilter, IImageFilter, ImageStream
# pylint: disable=C0103
logger = getLogger('myapp.tweetbot')

@unique
class ImageType(Enum):
    RAW = 1
    PLAN = 8
class AppImageFilter(IImageFilter):
    def __init__(self, image_type, hsv):
        super().__init__('AppImageFilter')
        self._contryMask = {'netzawar':(HSVcolor(175, 55, 0), HSVcolor(255, 255, 255)),
                            'casedria':(HSVcolor(53, 0, 0), HSVcolor(79, 255, 255)),
                            'geburand':(HSVcolor(120, 0, 100), HSVcolor(150, 255, 255)),
                            'hordine':(HSVcolor(24, 0, 249), HSVcolor(30, 255, 255)),
                            'ielsord':(HSVcolor(79, 0, 0), HSVcolor(112, 255, 255))}
        self.image_type = image_type
        self.hsv = hsv
    def filtered(self, stream):
        binary = stream

        # white color
        white = self.__getWhiteMasking(self.hsv)
        binary = cv2.bitwise_and(binary, binary, mask=white)
        if self.image_type == ImageType.PLAN:
            height, width = stream.shape[:2]
            cv2.rectangle(binary, (0, 0), (min(1000, width), height), (0, 0, 0), -1)
            return binary        
        lower, upper = HSVcolor(0, 0, 0), HSVcolor(30, 66, 255)
        binary = cv2.bitwise_and(binary, self.__inRange(self.hsv, lower, upper))
        #fez country color mask pattern
        #binary = self.bitwise_not(binary, self._contryMask['netzawar'])
        #binary = self.bitwise_not(binary, self._contryMask['geburand'])
        #binary = self.bitwise_not(binary, self._contryMask['ielsord'])
        #binary = self.bitwise_not(binary, self._contryMask['casedria'])
        #binary = self.bitwise_not(binary, self._contryMask['hordine'])
        # image out range fill
        height, width = stream.shape[:2]
        # todo setting.json
        clip_rect = Serializer.load_json('../resource/ocr.json')['clipping']
        start_x, start_y = clip_rect['start']
        end_x, end_y = clip_rect['end']
        binary = binary[start_y:end_x, start_x:end_y]
        return binary
    def bitwise_not(self, binary, mask_range):
        lower, upper = mask_range
        return cv2.bitwise_not(binary, binary, mask=self.__inRange(self.hsv, lower, upper))
    def __getWhiteMasking(self, hsv):
        sensitivity = 15
        lower = HSVcolor(0, 0, 255 - sensitivity)
        upper = HSVcolor(255, sensitivity, 255)
        return self.__inRange(hsv, lower, upper)
    def __inRange(self, hsv, lower, upper):
        return cv2.inRange(hsv, lower.to_np(), upper.to_np())
class DataProcessor(object):
    def __init__(self, name, image_type):
        self.__name = name
        self.image_type = image_type
        self.color = None
        self.__hsv = None
    @property
    def name(self):
        return self.__name
    @property
    def hsv(self):
        if self.__hsv is None:
            self.__hsv = cv2.cvtColor(self.color, cv2.COLOR_BGR2HSV)
        return self.__hsv
    def prepare(self):
        """
            @return color image
            @exception FileNotFoundError
        """
        filename = self.name
        zoom = 2
        c = cv2.imread(filename)
        if c is None:
            raise FileNotFoundError(self.name)
        self.color = cv2.resize(c, (c.shape[1]*zoom, c.shape[0]*zoom), interpolation=cv2.INTER_CUBIC)
        return self.color
    def batch(self):
        """
            masking)
                step1:color -> grayscale -> adaptiveThreshold
                step2:AppImageFilter#filtered
            @return {binary} image
        """
        stream = ImageStream()
        stream.data = self.color
        stream.addFilter(GrayScaleFilter())
        stream.addFilter(AdaptiveThresholdFilter())
        stream.addFilter(AppImageFilter(self.image_type, self.hsv))
        return stream.tofiltered()
    def tobinary(self, binary):
        """
            convert cv2.binary => Memory
            @param {cv2.binary} image
            @return {io.BytesIO} Memory
        """
        baseName = Path(self.name)
        ret, buf = cv2.imencode(baseName.suffix, binary)
        return BytesIO(np.array(buf).tostring())
