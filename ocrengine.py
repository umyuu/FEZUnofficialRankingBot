# -*- coding: utf-8 -*-
# library
import pyocr
import pyocr.builders
from PIL import Image
class DocumentCore(object):
    def __init__(self, document):
        self.document = document
    
class OCRDocument(object):
    def __init__(self, document):
        self.document = document
        self.rank1 = self.indexBy(0)
        self.rank2 = self.indexBy(1)
        self.rank3 = self.indexBy(2)
        self.rank4 = self.indexBy(3)
        self.rank5 = self.indexBy(4)
    def indexBy(self, index):
        d = dict()
        d['name'] = self.document[index]
        d['score'] = self.document[index + 5]
        return d   
class OCRText(object):
    def __init__(self, document):
        self.document = document
        self.content = document.content
        # recognize affter replace
        replaceText = dict()
        replaceText['丿レ'] = 'ル'
        replaceText['丿し'] = 'ル'
        replaceText['フ"'] = 'ブ'
        replaceText['フ`'] = 'ブ'
        replaceText['ーJ'] = 'リ'
        for before, after in replaceText.items():
            self.content = self.content.replace(before, after)
    def __getattr__(self, attr):
        return getattr(self.document, attr)
    def __str__(self):
        return self.content
class OCREngine(object):
    def __init__(self):
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            raise Exception('Tesseract non install')
        self.tool = tools[0]
        languages = self.tool.get_available_languages()
        if "jpn" not in languages:
            raise Exception('Tesseract NotFound :tessdata\jpn.traineddata')
        self.lang = 'jpn'
    def image_to_string(self, file, lang=None, builder=None):
        if lang is None:
            lang = self.lang
        if builder is None:
            builder = pyocr.builders.LineBoxBuilder(tesseract_layout=7)
        return self.tool.image_to_string(file, lang=lang, builder=builder)
    def recognize(self, file):
        if isinstance(file, str):
            with Image.open(file) as image:
                return self.recognize(image)
        result = []
        for document in self.image_to_string(file):
            result.append(OCRText(document))
        return OCRDocument(result)
