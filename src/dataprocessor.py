# -*- coding: utf-8 -*-
from logging import getLogger
from enum import Enum, unique
from pathlib import Path
from io import BytesIO
import os
#
import cv2
import numpy as np
#
from serializer import Serializer
from hsvcolor import HSVcolor
from events import Filters
# pylint: disable=C0103
logger = getLogger('myapp.tweetbot')

@unique
class ImageType(Enum):
    RAW = 1
    PLAN = 8
class DataProcessor(object):
    """
        DataProcessor is image convert.
        step1.
            cv2.resize zooming scalle 2
        step2.
            a. image(color) => cv2.grayscale => cv2.adaptiveThreshold
            b. image(color) => hsv
            c. addWhiteMasking(a, b)  => step3
        step3.
            a. clipping image.
    """
    def __init__(self, media, image_type, save_image=False):
        self.__media = media
        self.image_type = image_type
        self.color = None
        self.__hsv = None
        self.save_image = save_image
        # image => ocr image.
        self.filter = Filters()
        self.filter += self.base_filtered
        self.filter += self.addWhiteMasking
        if image_type == ImageType.RAW:
            self.filter += self.filtered
        else:
            self.filter += self.clipping_filtered
    @property
    def media(self):
        return self.__media
    @property
    def hsv(self):
        if self.__hsv is None:
            self.__hsv = cv2.cvtColor(self.color, cv2.COLOR_BGR2HSV)
        return self.__hsv
    def prepare(self):
        """
            @return {color} image
            @exception FileNotFoundError
        """
        filename = self.media
        zoom = 2
        c = cv2.imread(filename)
        if c is None:
            raise FileNotFoundError(self.media)
        self.color = cv2.resize(c, (c.shape[1]*zoom, c.shape[0]*zoom), interpolation=cv2.INTER_CUBIC)
        return self.color
    def batch(self):
        """
            @return {binary} image
        """
        result = self.filter(self.color)
        if self.save_image:
            cv2.imwrite('../temp/ocr_{0}'.format(os.path.basename(self.media)), result)
        return result
    def base_filtered(self, sender, ev):
        result = cv2.cvtColor(sender, cv2.COLOR_BGR2GRAY)
        result = cv2.adaptiveThreshold(result, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 3)
        if self.save_image:
            cv2.imwrite('../temp/color{0}'.format(os.path.basename(self.media)), sender)
            cv2.imwrite('../temp/base_filtered{0}'.format(os.path.basename(self.media)), result)
        return result
    def addWhiteMasking(self, sender, ev):
        """
            color masking
        """
        binary = sender
        # white color
        sensitivity = 15
        lower = HSVcolor(0, 0, 255 - sensitivity)
        upper = HSVcolor(255, sensitivity, 255)
        white = cv2.inRange(self.hsv, lower.to_np(), upper.to_np())
        binary = cv2.bitwise_and(binary, binary, mask=white)
        cv2.imwrite('../temp/addWhiteMasking{0}'.format(os.path.basename(self.media)), binary)
        return binary
    def image_clipping(self, sender, ev):
        pass
    def clipping_filtered(self, sender, ev):
        stream = sender
        binary = stream
        height, width = stream.shape[:2]
        cv2.rectangle(binary, (0, 0), (min(1000, width), height), (0, 0, 0), -1)
        return binary
    def filtered(self, sender, ev):
        stream = sender
        binary = stream

        lower, upper = HSVcolor(0, 0, 0), HSVcolor(30, 66, 255)
        binary = cv2.bitwise_and(binary, self.__inRange(self.hsv, lower, upper))
        # image out range fill
        height, width = stream.shape[:2]
        clip_rect = Serializer.load_json('../resource/ocr.json')['clipping']
        start_x, start_y = clip_rect['start']
        end_x, end_y = clip_rect['end']
        binary = binary[start_y:end_x, start_x:end_y]
        return binary
    def bitwise_not(self, binary, mask_range):
        lower, upper = mask_range
        return cv2.bitwise_not(binary, binary, mask=self.__inRange(self.hsv, lower, upper))
    def __inRange(self, hsv, lower, upper):
        return cv2.inRange(hsv, lower.to_np(), upper.to_np())
    def tobinary(self, binary):
        """
            convert cv2.binary => Memory
            @param {cv2.binary} image
            @return {io.BytesIO} Memory
        """
        baseName = Path(self.media)
        ret, buf = cv2.imencode(baseName.suffix, binary)
        return BytesIO(np.array(buf).tostring())
