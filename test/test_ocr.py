# -*- coding: utf-8 -*-
#
import pytest
import numpy as np
# pylint: disable=W0611
import conftest
# pylint: enable=W0611
from serializer import Serializer
from ocrengine import OCRDocument
from xmldocument import XMLDocument

# pylint: disable=C0103
class TestClass(object):
    def test_splitText_1(self):
        ocr_text = ['ゲフ`ランド帝国 es34。-ァ。',
                    'ネッァワ丿レ王国 66sg4.6s',
                    'ホ丿しディン王国 66346-4s',
                    'ヵセドリア連合王目 65フ4。.ェ。',
                    'ェ丿しソ一 ド王目 63263.60']
        self.decodeText(ocr_text)
    def test_splitText_2(self):
        ocr_text = ['ネツァワ丿し王国',
                    'ホ丿レテ〝イン王国',
                    '力セドー丿ア連合王国',
                    'ゲフ`「ラン ド帝国',
                    '工丿レソ一 ド王国',
                    'ーー6462.30',
                    'ーー3883.60',
                    'ー09730・ー0',
                    'ー〔}8ー募)()-7()',
                    'ー〔}(】548-()()',
                    'p。int' ,
                    'p。iーーt',
                    'L)。iーーt',
                    'ー}。麦ーーt',
                    'ー}。麦ーーt']
        self.decodeText(ocr_text)
    def decodeText(self, data):
        """
            @param {list<string>} ocrText
        """
        json_data = Serializer.load_json('../resource/ocr.json')
        doc = OCRDocument(json_data)
        maxLengh = len(data)
        xml = doc.xml
        decode = xml.addChild(xml.body, 'decode')
        for index in range(5):
            name_score = doc.get_name_score(data, index, maxLengh)
            content = doc.splitText(name_score)
            xml.addChild(decode, 'row', content)
        print(XMLDocument.toPretty(xml.root))
if __name__ == '__main__':
    pytest.main("--capture=sys")
