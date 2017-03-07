# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
import os
from datetime import datetime
#
import serializer
from ocrengine import OCREngine
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
    def getResult(self, src):
        """
            @return OCRDocument
        """
        pro = DataProcessor(src, ImageType.RAW)
        if pro.prepare() is None:
            logger.error('image error:{0}'.format(src))
            return None
        batch = pro.batch()
        temp_file_name = pro.save_tempfile(batch)
        
        doucument = self.ocr.recognize(temp_file_name)
        # todo: ocr corpus classifier
        os.remove(temp_file_name)
        with serializer.open_stream('../temp/corpus.txt', mode='a') as file:
            header = '#' + datetime.now().strftime('%F %T.%f')[:-3] + '\n'
            file.write(header)
            file.write('\n'.join(doucument.names()))
            file.write('\n')
        
        return doucument

def main():
    config = serializer.load_json('../resource/setting.json')
    r = Ranking(config)
    # benchMark
    ele = ['../backup/hints/201702190825_0565e4fcbc166f00577cbd1f9a76f8c7.png',
        #    '../backup/test/201702191909_ac08ccbbb04f2a1feeb4f8aaa08ae008.png',
        #     '../backup/test/201702192006_2e268d7508c20aa00b22dfd41639d65e.png',
        ] * 2
    for l in ele:
        logger.info(l)
        ranking = r.getResult(l)
        logger.info(ranking)
if __name__ == "__main__":
    main()
