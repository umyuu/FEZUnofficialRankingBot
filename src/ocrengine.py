# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
#
import pyocr
import pyocr.builders
from PIL import Image
#
import serializer
from sklearn.naive_bayes import MultinomialNB

logger = getLogger('myapp.tweetbot')
if __name__ == "__main__":
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)

class OCRDocument(object):
    def __init__(self):
        self.__ranking = []
        self.__raw = []
        self.translate = serializer.load_json('../resource/ocr.json')['translate']
    @property
    def ranking(self):
        """
            ocr text ranking
        """
        return self.__ranking
    def indexByContents(self, index, contents):
        """
            ocr filed pair
            @retunr name score
        """
        return {"name":contents[index], "score":contents[index + 5]}
    def parse(self, documents):
        """
            OCR data.
                parse & pickup
            @params documents image_to_string result data
            @return rawData
        """
        result = []
        for i, document in enumerate(documents):
            trans = self.translate['name']
            if i > 5:
                trans = self.translate['score']
            result.append(OCRText(document, trans))
        for i in range(5):
            content = self.indexByContents(i, result)
            self.__ranking.append(content)
            self.__raw.append(content)
        return result
    @property
    def raw(self):
        """
            ocr text raw
        """
        return self.__raw
    def dump(self):
        """
            developers method.
        """
        for text in self.__ranking:
            logger.info('{name}/{score}'.format_map(text))
class OCRText(object):
    def __init__(self, document, trans):
        self.document = document
        self.content = document.content
        # recognize translate replace
        for before, after in trans.items():
            self.content = self.content.replace(before, after)
    def __getattr__(self, attr):
        return getattr(self.document, attr)
    def __str__(self):
        return self.content
class OCREngine(object):
    """
        OCREngine: call Tesseract-OCR.
    """
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
        """
            call pyocr#image_to_string
        """
        if lang is None:
            lang = self.lang
        if builder is None:
            builder = pyocr.builders.LineBoxBuilder(tesseract_layout=7)
        return self.tool.image_to_string(file, lang=lang, builder=builder)
    def recognize(self, file):
        if isinstance(file, str):
            with Image.open(file) as image:
                return self.recognize(image)
        
        doc = OCRDocument()
        doc.parse(self.image_to_string(file))
        return doc

def main():
    ocr = OCREngine()
    temp_file_name = '../base_binary.png'
    doc = ocr.recognize(temp_file_name)
    doc.dump()
    names = []
    for n in doc.raw:
        names.append(str(n['name']))
       
        
    logger.info(names)
    data = serializer.load_csv('../resource/corpus.txt')
    x_train = []
    y_train = []
    for text in data:
        x_train.append(text[1])
        y_train.append(text[0])
    print(data)
    print(x_train)
    print(y_train)
    clf = MultinomialNB(alpha=0.1)
    #clf.fit(x_train, y_train)
    
    #document.dump()
if __name__ == "__main__":
    main()
