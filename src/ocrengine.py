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
    def __init__(self, settings):
        """
            @param {json}settings
        """
        self.xml = XMLDocument('tweetbot')
        self.translate = settings['translate']
        self.__countries = settings['translate']['country']
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
            @param {list}text
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
        name = text[index]
        name = self.textTransrate(name, self.translate['name'])
        if maxLengh != offset:
            score = text[index + offset]
            score = score[:score.rfind(' ')]
            score = self.textTransrate(score, self.translate['score'])
            return self.createElement(name.replace(' ',''), score)
        rindex = name.rfind(' ')
        score = name[rindex + 1:]
        score = self.textTransrate(score, self.translate['score'])
        return self.createElement(name[:rindex].replace(' ',''), score)
    def createElement(self, name, score):
        return {"name":name, "score":score}
    def textTransrate(self, text, trans):
        """
            @param {string}text
                   {dict}trans
        """
        for before, after in trans.items():
            text = text.replace(before, after)
        return text
    def parse(self, documents):
        """
            OCR data.
                parse & pickup
            @param documents image_to_string result data
        """
        xml = self.xml
        result, length = self.addOCRData(documents) 
        decode = xml.addChild(xml.body, 'decode')
        for i in range(5):
            content = self.splitText(result, i, length)
            xml.addChild(decode, 'row', content)
        print(XMLDocument.toPrettify(xml.root))
    def addOCRData(self, documents):
        """
            @param {list}documents ocr data
            @return {list}result,{int}length
        """
        xml = self.xml
        ocr = xml.addChild(xml.body, 'ocr')
        result = []
        for document in documents:
            result.append(document.content)
            child = xml.addChild(ocr, 'row')
            child.text = document.content
        length = len(result)
        ocr.set('length', str(length))
        #print(XMLDocument.toPrettify(xml.root))
        return result, length
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
        json_data = Serializer.load_json('../resource/ocr.json')
        self.__settings = json_data
        self.lang = json_data['lang']
        self.tesseract_layout = json_data['pagesegmode']
        if self.lang not in languages:
            raise Exception('Tesseract NotFound :tessdata\\{0}.traineddata'.format(self.lang))
    @property
    def Settings(self):
        return self.__settings
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

        doc = OCRDocument(self.__settings)
        doc.parse(self.image_to_string(file))
        return doc

def main():
    ocr = OCREngine()
    temp_file_name = '../base_binary.png'
    
    #temp_file_name = '../temp/ocr_2017-03-12_0443_Geburand.png'
    doc = ocr.recognize(temp_file_name)
    doc.dump()
    print(doc.names())
if __name__ == "__main__":
    main()
