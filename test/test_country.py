# -*- coding: utf-8 -*-
import os
#
import pytest
import numpy as np
# pylint: disable=W0611
import conftest
# pylint: enable=W0611

from serializer import Serializer
from naivebayes import NaiveBayes

# pylint: disable=C0103
class TestClass(object):
    def test_loadSettingFile(self):
        basepath = '../resource/'
        config = Serializer.load_json(os.path.join(basepath, 'setting.json'))
        Serializer.load_ini(config['AUTH']['TWITTER'])
        Serializer.load_json(os.path.join(basepath, 'ocr.json'))
        Serializer.load_csv(os.path.join(basepath, 'corpus.tsv'))
    #@pytest.mark.skipif("True")
    def test_naivebayes_compare(self):
        basepath = '../resource/'
        naivebayes = NaiveBayes()
        json_data = Serializer.load_json(os.path.join(basepath, 'ocr.json'))
        naivebayes.human_labels = json_data['translate']['country']
        x_list = ['ネツァワル王国','カセドリア連合王国','ゲブランド帝国','ホルデイン王国','エルソード王国']
        
        print(json_data['translate']['country'])
        out = naivebayes.predict_all(x_list)
        for i, y in enumerate(out):
            if x_list[i] != y:
                raise Exception('compare x:{0},predict:{1}'.format(x_list[i], y))
    def test_naivebayes_labeling(self):
        naivebayes = NaiveBayes()
        corpus = Serializer.load_csv('../resource/corpus.tsv')
        data = []
        target = []
        for row in corpus:
            data.append(str(row[0]))
            t = int(row[1])
            if t > 5:
                raise Exception(t)
            target.append(t)
        np.array(target, dtype=np.uint8, ndmin=1)
        
if __name__ == '__main__':
    pytest.main("--capture=sys")
