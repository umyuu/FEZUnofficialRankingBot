# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
from enum import Enum, unique
#
import pyocr
import pyocr.builders
from PIL import Image

logger = getLogger('myapp.tweetbot')
if __name__ == "__main__":
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)

@unique
class OCRField(Enum):
    TEXT = 1
    NUMBER = 2
class DocumentCore(object):
    def __init__(self, document):
        self.document = document
        self.__fields = dict()
    @property
    def fields(self):
        return self.__fields
    def addField(self, name, attribute):
        if not isinstance(attribute, OCRField):
            raise NotImplementedError()
        self.__fields[name] = attribute
        return self
class OCRDocument(DocumentCore):
    def __init__(self, document):
        super().__init__(document)
        self.addField('name', OCRField.TEXT)
        self.addField('score', OCRField.NUMBER)
    def insert(self, text):
        self.documents = text
        self.contents = []
        for document in self.documents:
            self.contents.append(document.content)
        
        self.parseElements()
        print(self.rank1)
        return self
    def parseElements(self):
        self.rank1 = self.indexByContents(0, self.contents)
        self.rank2 = self.indexByContents(1, self.contents)
        self.rank3 = self.indexByContents(2, self.contents)
        self.rank4 = self.indexByContents(3, self.contents)
        self.rank5 = self.indexByContents(4, self.contents)
        return self
    def indexByContents(self, index, contents):
        d = dict()
        d['name'] = contents[index]
        d['score'] = contents[index + 5]
        return d
    def readContent(self, text, attribute):
        if attribute is None:
            pass
        else:
            pass
        
            
        return text
    def indexBy(self, index):
        d = dict()
        d['name'] = self.document[index]
        d['score'] = self.document[index + 5]
        return d
    def read(self):
        self.rank1 = self.indexBy(0)
        self.rank2 = self.indexBy(1)
        self.rank3 = self.indexBy(2)
        self.rank4 = self.indexBy(3)
        self.rank5 = self.indexBy(4)
        return self
    def parse(self, documents):
        result = []
        for document in documents:
            result.append(OCRText(document))
        return result
    def dump(self):
        for text in [self.rank1, self.rank2, self.rank3, self.rank4, self.rank5]:
            logger.info('{name}/{score}'.format_map(text))
class OCRText(object):
    def __init__(self, document):
        self.document = document
        self.content = document.content
        # recognize affter replace
        translate = dict()
        translate['丿レ'] = 'ル'
        translate['丿し'] = 'ル'
        translate['フ"'] = 'ブ'
        translate['フ`'] = 'ブ'
        translate['ーJ'] = 'リ'
        translate['ー丿'] = 'リ'
        translate['ー'] = '.'
        for before, after in translate.items():
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
        return OCRDocument(result).read()
    def recognize_refact(self, file):
        if isinstance(file, str):
            with Image.open(file) as image:
                return self.recognize_refact(image)
        
        doc = OCRDocument(None)
        result = doc.parse(self.image_to_string(file))
        doc.insert(self.image_to_string(file))
        return result


def main():
    ocr = OCREngine()
    temp_file_name = '../base_binary.png'
    document = ocr.recognize_refact(temp_file_name)
    print(document)
    #document.dump()
if __name__ == "__main__":
    main()
