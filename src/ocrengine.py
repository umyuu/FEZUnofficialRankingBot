# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
#
import pyocr
import pyocr.builders
from PIL import Image
#
from serializer import Serializer

# pylint: disable=C0103
logger = getLogger('myapp.tweetbot')
if __name__ == "__main__":
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)

class OCRDocument(object):
    """
        data convert.
        in:OCREngine#recognize data
        out:application require data
    """
    def __init__(self):
        self.__ranking = []
        self.__raw = []
        json_data = Serializer.load_json('../resource/ocr.json')
        self.translate = json_data['translate']
        self.__countries = json_data['translate']['country']
    @property
    def ranking(self):
        """
            @return {list} ocr text ranking
        """
        return self.__ranking
    def indexByContents(self, contents, index, offset=5):
        """
            ocr text replaced
            created filed pair
            @param {string}contents
                   {int}index
                   {int}offset
            @return {dict} name score
        """
        # exsample) input           => output
        #           工ルソ一 ド王国    => 工ルソ一ド王国
        name = str(contents[index]).replace(' ','')
        # \d+.\d+ [point] => \d+.\d+
        # exsample) input           => output
        #           228993.70 point => 228993.70
        score = str(contents[index + offset])
        score = score[:score.rfind(' ')]
        return {"name":name, "score":score}
    def parse(self, documents):
        """
            OCR data.
                parse & pickup
            @param documents image_to_string result data
            @return {list} rawData
        """
        result = []
        for i, document in enumerate(documents):
            trans = self.translate['name']
            if i > 5:
                trans = self.translate['score']
            result.append(OCRText(document, trans))
        for i in range(5):
            content = self.indexByContents(result, i)
            self.__ranking.append(content)
            self.__raw.append(content)
        return result
    @property
    def countries(self):
        """
            @return {dict} __countries
        """
        return self.__countries
    @property
    def raw(self):
        """
            @return {list} ocr text raw
        """
        return self.__raw
    def names(self):
        """
            @return {list} ocr names
        """
        result = []
        for n in self.raw:
            result.append(str(n['name']))
        return result
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
            @param {PIL.Image} file
                   {string}    lang
                   {pyocr.builder} builder
            call pyocr#image_to_string
        """
        if lang is None:
            lang = self.lang
        if builder is None:
            builder = pyocr.builders.LineBoxBuilder(tesseract_layout=7)
        return self.tool.image_to_string(file, lang=lang, builder=builder)
    def recognize(self, file):
        """
            @params {string},{PIL.Image} file
            @return {OCRDocument}
        """
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

if __name__ == "__main__":
    main()
