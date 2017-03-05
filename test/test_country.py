# -*- coding: utf-8 -*-
import os
#
import pytest
#
import serializer

class TestClass(object):
    def test_loadSettingFile(self):
        basepath = '../resource/'
        config = serializer.load_ini(os.path.join(basepath, 'setting.ini'))
        serializer.load_ini(config['AUTH']['TWITTER'])
        serializer.load_json(os.path.join(basepath, 'ocr.json'))
if __name__ == '__main__':
    pytest.main("--capture=sys")