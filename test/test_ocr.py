# -*- coding: utf-8 -*-
import os
#
import pytest
import numpy as np
# pylint: disable=W0611
import conftest
# pylint: enable=W0611
import serializer
from naivebayes import NaiveBayes

# pylint: disable=C0103
class TestClass(object):
    def test_loadSettingFile(self):
        basepath = '../resource/'
        config = serializer.load_json(os.path.join(basepath, 'setting.json'))
        serializer.load_ini(config['AUTH']['TWITTER'])
    def test_naivebayes(self):
        pass
if __name__ == '__main__':
    pytest.main("--capture=sys")
