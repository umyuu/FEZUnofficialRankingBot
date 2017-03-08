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
        serializer.load_json(os.path.join(basepath, 'ocr.json'))
        serializer.load_csv(os.path.join(basepath, 'corpus.txt'))
        serializer.load_np(os.path.join(basepath, 'labels.txt'), dtype=np.uint8)
    def test_naivebayes_compare(self):
        basepath = '../resource/'
        naivebayes = NaiveBayes()
        json_data = serializer.load_json(os.path.join(basepath, 'ocr.json'))
        x_list = ['ネツァワル王国','カセドリア連合王国','ゲブランド帝国','ホルデイン王国','エルソード王国']
        out = naivebayes.predict_all(x_list, json_data['translate']['country'])
        for i, y in enumerate(out):
            if x_list[i] != y:
                raise Exception('compare x:{0},predict:{1}'.format(x_list[i], y))
if __name__ == '__main__':
    pytest.main("--capture=sys")
