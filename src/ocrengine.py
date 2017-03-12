# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
#
import pyocr
import pyocr.builders
from PIL import Image
#
from serializer import Serializer
from xmldocument import XMLDocument
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
        self.xml = XMLDocument('tweetbot')
        json_data = Serializer.load_json('../resource/ocr.json')
        self.translate = json_data['translate']
        self.__countries = json_data['translate']['country']
    @property
    def ranking(self, xpath='./body/decode/row'):
        """
            @return {list} ocr text ranking copy
        """
        result = []
        for row in self.xml.findall(xpath):
            d = self.createElement(row.find('name').text, row.find('score').text)
            result.append(d)
        return result
    def splitText(self, text, index, maxLengh, offset=5):
        """
            ocr text replaced
            created Field pair
            @param {string}text
                   {int}index
                   {int}maxLengh  ocr decord max length=5
                   {int}offset
            @return {dict} name score
        """
        # exsample) input           　=> output
        # □name
        #           工ルソ一 ド王国    　=> 工ルソ一ド王国
        # □score　　　　\d+.\d+ [point] => \d+.\d+
        #           228993.70 point => 228993.70
        name = str(text[index])
        if maxLengh != offset:
            score = str(text[index + offset])
            score = score[:score.rfind(' ')]
            return {"name":name.replace(' ',''), "score":score}
        rindex = name.rfind(' ')
        return {"name":name[:rindex].replace(' ',''), "score":name[rindex + 1:]}
    def createElement(self, name, score):
        return  {"name":name, "score":score}
    def parse(self, documents):
        """
            OCR data.
                parse & pickup
            @param documents image_to_string result data
        """
        xml = self.xml
        result = self.addOCRData(documents) 
        decode = xml.addChild(xml.body, 'decode')
        length = len(result)
        for i in range(5):
            content = self.splitText(result, i, length)
            xml.addChild(decode, 'row', content)
        #print(XMLDocument.toPrettify(xml.root))
    def addOCRData(self, documents):
        xml = self.xml
        ocr = xml.addChild(xml.body, 'ocr')
        result = []
        for i, document in enumerate(documents):
            trans = self.translate['name']
            if i > 5:
                trans = self.translate['score']
            ocr_decode = OCRText(document, trans)
            result.append(ocr_decode)
            child = xml.addChild(ocr, 'row')
            child.text = document.content
        ocr.set('length', str(len(result)))
        #print(XMLDocument.toPrettify(xml.root))
        return result
    def changeNames(self, change):
        for i, row in enumerate(self.xml.findall("./body/decode/row")):
            row.find('name').text = change[i]
    @property
    def countries(self):
        """
            @return {dict} __countries
        """
        return self.__countries
    def names(self):
        """
            name list
                order ranking
            @return {list} ocr names
        """
        result = []
        for row in self.xml.findall("./body/decode/row"):
            result.append(row.find('name').text)
        return result
    def dump(self, xpath='./body/decode/row'):
        """
            developers method.
        """
        for row in self.xml.findall(xpath):
            logger.info('%s/%s', row.find('name').text, row.find('score').text)
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
        self.tesseract_layout = Serializer.load_json('../resource/ocr.json')['pagesegmode']
        
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
            builder = pyocr.builders.LineBoxBuilder(tesseract_layout=self.tesseract_layout)
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
    #temp_file_name = '../base_binary.png'
    
    temp_file_name = '../temp/ocr_2017-03-12_0443_Geburand.png'
    doc = ocr.recognize(temp_file_name)
    doc.dump()
    print(doc.names())
if __name__ == "__main__":
    main()
