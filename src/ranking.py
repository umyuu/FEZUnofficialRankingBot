# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
import os
import tempfile
from io import BytesIO
from datetime import datetime
#
from serializer import Serializer
from ocrengine import OCREngine
from naivebayes import NaiveBayes
from dataprocessor import DataProcessor, ImageType

logger = getLogger('myapp.tweetbot')
if __name__ == "__main__":
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)


class Ranking(object):
    def __init__(self, config):
        self.ocr = OCREngine()
        self.naivebayes = NaiveBayes()
        self.naivebayes.human_labels = self.ocr.settings['translate']['country']

    def create_TemporyFile(self, buffer, verbose=False):
        """
            
            @param {io.BytesIO}buffer
                   {bool}verbose
            @return {string}create file tempory file
        """
        temp_file_name = ''
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(buffer.getvalue())
            temp_file_name = temp.name
            if verbose:
                logger.info(temp_file_name)
        return temp_file_name

    def getResult(self, src, save_image=False):
        """
            @param {string} src
                   {bool}save_image output debug image
            @return {OCRDocument} doucument
        """
        pro = DataProcessor(src, ImageType.RAW, save_image=save_image)
        if pro.prepare() is None:
            logger.error('image error:{0}'.format(src))
            return None
        buffer = pro.tobinary(pro.batch())
        temp_file_name = self.create_TemporyFile(buffer, True)

        document = self.ocr.recognize(temp_file_name)
        os.remove(temp_file_name)
        
        output = '#' + datetime.now().strftime('%F %T.%f')[:-3] + '\n'
        output += '\n'.join(document.names()) + '\n'
        with Serializer.open_stream('../temp/corpus.txt', mode='a') as file:
            file.write(output)

        # ocr corpus data -> NaiveBayes classifier
        # ranking name swap
        change = self.naivebayes.predict_all(document.names())
        #doucument.changeNames(change)

        document.dump()
        return document


def main():
    config = Serializer.load_json('../resource/setting.json')
    r = Ranking(config)
    # benchMark
    ele = ['../backup/hints/201702190825_0565e4fcbc166f00577cbd1f9a76f8c7.png',
           #'../images/backup/2017-03-12_0443_Geburand.png',
        #     '../backup/test/201702192006_2e268d7508c20aa00b22dfd41639d65e.png',
        ] * 1
    for media in ele:
        logger.info(media)
        document = r.getResult(media, True)
        logger.info(document.ranking)
if __name__ == "__main__":
    main()
