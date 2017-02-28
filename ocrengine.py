# -*- coding: utf-8 -*-
import pyocr
import pyocr.builders

class OCRText(object):
    def __init__(self, document):
        self.document = document
        self.content = document.content
        # recognize affter replace
        replaceText = dict()
        replaceText['丿レ'] = 'ル'
        replaceText['丿し'] = 'ル'
        replaceText['フ"'] = 'ブ'
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
        
    def image_to_string(self, file):
        return self.tool.image_to_string(file,
                                    lang=self.lang,
                                    builder=pyocr.builders.LineBoxBuilder(tesseract_layout=7))
    def recognize(self, file):
        result = []
        for document in self.image_to_string(file):
            result.append(OCRText(document))
        return result