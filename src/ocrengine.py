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
        self.xpath_findkey = './body/ranking/row'
    @property
    def ranking(self):
        """
            
            @return {list.dict<string,string>} ocr text ranking copy
                    order point
        """
        result = []
        for row in self.xml.findall(self.xpath_findkey):
            d = self.createElement(row.find('name').text, row.find('point').text)
            result.append(d)
        assert len(result) != 0
        return result
    def get_name_point(self, data, index, maxLengh):
        """
            ocr data => split name, point
            □name
                工ルソ一 ド王国    　=> 工ルソ一ド王国
            @param {list}data
                   {int}index
                   {int}maxLengh
            @return {list} name, point
        """
        name_point = []
        name = data[index]
        if maxLengh == 5:
            splits = name.split(' ')
            name_point.append(''.join(splits[:-1]))
            name_point.append(''.join(splits[-1:]))
        else:
            name_point.append(name)
            name_point.append(data[index + 5])
        return name_point
    def splitText(self, name_point):
        name = name_point[0]
        point = name_point[1]
        name = self.textTransrate(name, self.translate['name'])
        point = self.textTransrate(point, self.translate['point'])
        return self.createElement(name, point)
    def createElement(self, name, point):
        return {"name":name, "point":point}
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
        # Create 1st Node
        decode = xml.addChild(xml.body, 'ranking')
        # Create 2nd Node
        data, maxLengh = self.addOCRData(documents, xml)
        # decode
        for i in range(5):
            name_point = self.get_name_point(data, i, maxLengh)
            content = self.splitText(name_point)
            child = xml.addChild(decode, 'row')
            child.set('order', str(i))
            xml.addDict(child, content)
        print(xml.toPretty())
    def addOCRData(self, documents, xml):
        """
            @param {list}documents ocr data
                   {XMLDocument}xml
            @return {list}result,{int}length
        """
        ocr = xml.addChild(xml.body, 'ocr')
        result = []
        for i, document in enumerate(documents):
            result.append(document.content)
            child = xml.addChild(ocr, 'row')
            child.text = document.content
            child.set('order', str(i))
        length = len(result)
        #print(xml.toPretty())
        return result, length
    def changeNames(self, change):
        for i, row in enumerate(self.xml.findall(self.xpath_findkey)):
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
        for row in self.xml.findall(self.xpath_findkey):
            result.append(row.find('name').text)
        assert len(result) != 0
        return result
    def dump(self):
        """
            developers method.
        """
        for row in self.xml.findall(self.xpath_findkey):
            logger.info('%s/%s', row.find('name').text, row.find('point').text)
class OCRException(Exception):
    """
        OCR Exception
    """
    pass
class OCREngine(object):
    """
        OCREngine: call Tesseract-OCR.
    """
    def __init__(self):
        """
            
            @exception OCRException
                a,ocr noninstall
                b,traineddata NotFound
        """
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            raise OCRException('Tesseract non install')
        self.tool = tools[0]
        languages = self.tool.get_available_languages()
        json_data = Serializer.load_json('../resource/ocr.json')
        self.__settings = json_data
        self.lang = json_data['lang']
        self.tesseract_layout = json_data['pagesegmode']
        if self.lang not in languages:
            raise OCRException('Tesseract NotFound :tessdata\\{0}.traineddata'.format(self.lang))
    @property
    def settings(self):
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
        decode = xml.addChild(xml.body, 'ranking')
        for index in range(5):
            name_point = doc.get_name_point(data, index, maxLengh)
            print(name_point)
            content = doc.splitText(name_point)
            child = xml.addChild(decode, 'row')
            xml.addDict(child, content)
        print(xml.toPretty())

def main():
    ocr = OCREngine()
    temp_file_name = '../base_binary.png'
    #temp_file_name = '../temp/ocr_2017-03-12_0443_Geburand.png'
    
    ocr.test_splitText_2()
    
    doc = ocr.recognize(temp_file_name)
    doc.dump()
    print(doc.names())
if __name__ == "__main__":
    main()
