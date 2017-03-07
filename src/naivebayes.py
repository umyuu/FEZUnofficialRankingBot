# -*- coding: utf-8 -*-
"""
    naivebayes.py
    naivebayes classifier
"""
from logging import getLogger, StreamHandler, DEBUG
#
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
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
    def __init__(self, vectorizer):
        self.__vectorizer = vectorizer
        self.data = serializer.load_csv('../resource/corpus.txt')
        self.labels = serializer.load_np('../resource/labels.txt', dtype=np.uint8)
        self.model = MultinomialNB(alpha=0.1)
        train = []
        for row in self.data:
            train.append(row[0])
        docs = np.array(train)
        print(docs)
        vecs = vectorizer.fit_transform(docs)
        
        self.model.fit(vecs, self.labels)
        
        logger.info(self.data)
        logger.info(self.labels)
    @property
    def vectorizer(self):
        return self.__vectorizer
    def predict(self, x):
        return self.model.predict(x)

def main():
    ocr = OCREngine()
    temp_file_name = '../base_binary.png'
    doc = ocr.recognize(temp_file_name)
    doc.dump()
    logger.info(doc.names())
    np.set_printoptions(precision=2)
    naivebayes = NaiveBayes(TfidfVectorizer(use_idf=True))
    
    predict_data = np.array(doc.names())
    for i, v in enumerate(naivebayes.vectorizer.transform(predict_data)):
        predict = naivebayes.predict(v)[0]
        name = doc.countries[str(predict)]
        logger.info('%s -> 推定: %s', predict_data[i], name)  

    #document.dump()
if __name__ == "__main__":
    main()
