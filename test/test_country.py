# -*- coding: utf-8 -*-
import os
#
import pytest
import numpy as np
#
import serializer

class TestClass(object):
    def test_loadSettingFile(self):
        basepath = '../resource/'
        config = serializer.load_json(os.path.join(basepath, 'setting.json'))
        serializer.load_ini(config['AUTH']['TWITTER'])
        serializer.load_json(os.path.join(basepath, 'ocr.json'))
        serializer.load_csv(os.path.join(basepath, 'corpus.txt'))
        serializer.load_np(os.path.join(basepath, 'labels.txt'), dtype=np.uint8)
if __name__ == '__main__':
    pytest.main("--capture=sys")