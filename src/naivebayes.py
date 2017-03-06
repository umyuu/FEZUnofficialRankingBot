# -*- coding: utf-8 -*-
"""
    naivebayes.py
    naivebayes classifier
"""
from logging import getLogger, StreamHandler, DEBUG
#
from sklearn.naive_bayes import MultinomialNB
#
import serializer
from ocrengine import OCREngine

logger = getLogger('myapp.tweetbot')
if __name__ == "__main__":
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)

class NaiveBayes(object):
    def __init__(self):
        pass
    
def main():
    ocr = OCREngine()
    temp_file_name = '../base_binary.png'
    doc = ocr.recognize(temp_file_name)
    doc.dump()
    names = []
    for n in doc.raw:
        names.append(str(n['name']))
       
        
    logger.info(names)
    x_train = serializer.load_csv('../resource/corpus.txt')
    y_train = serializer.load_csv('../resource/labels.txt')
    print(x_train)
    print(y_train)
    clf = MultinomialNB(alpha=0.1)
    #clf.fit(x_train, y_train)
    
    #document.dump()
if __name__ == "__main__":
    main()
