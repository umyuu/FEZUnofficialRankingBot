# -*- coding: utf-8 -*-
import numpy as np

# pylint: disable=C0103
class HSVcolor(object):
    """
        hsv color code class
    """
    __slots__ = ['h', 's', 'v']
    def __init__(self, h=0, s=0, v=0):
        self.h = h
        self.s = s
        self.v = v
    def __str__(self):
        return ','.join([str(self.h), str(self.s), str(self.v)])
    def to_np(self):
        """
            hsvcolor code to np array
        """
        return np.array([self.h, self.s, self.v])
