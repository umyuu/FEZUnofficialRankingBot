# -*- coding: utf-8 -*-
"""
    naivebayes.py
    naivebayes classifier
"""
from logging import getLogger, StreamHandler, DEBUG
import itertools
#
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_val_score
#
import serializer
from ocrengine import OCREngine

# pylint: disable=C0103
logger = getLogger('myapp.tweetbot')
if __name__ == "__main__":
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)

class NaiveBayes(object):
    """
        NaiveBayes Classifier.
        use sklearn.naive_bayes.MultinomialNB
    """
    def __init__(self, vectorizer=None):
        if vectorizer is None:
           vectorizer = TfidfVectorizer(use_idf=True)
        self.__vectorizer = vectorizer
        corpus = serializer.load_csv('../resource/corpus.txt')
        corpus_flat = list(itertools.chain.from_iterable(corpus))
        self.features = vectorizer.fit_transform(np.array(corpus_flat))
        self.labels = serializer.load_np('../resource/labels.txt', dtype=np.uint8)
        self.model = MultinomialNB(alpha=0.1)
        self.model.fit(self.features, self.labels)
    @property
    def vectorizer(self):
        """
            @return {Vectorizer}
        """
        return self.__vectorizer
    def predict(self, x):
        """
            predict params x
            @param {string},{np.array} x
            @return result
        """
        if isinstance(x, str):
            v = self.vectorizer.transform(np.array(x, ndmin=1))
            return self.model.predict(v)

        return self.model.predict(x)
    def predict_all(self, predicts, pair):
        """
            mapping
            @param {list} predicts
                   {dict} pair
            @return {list} value
        """
        result = []
        predict_data = np.array(predicts, ndmin=1)
        for i, v in enumerate(self.vectorizer.transform(predict_data)):
            predict = self.predict(v)[0]
            result.append(pair[str(predict)])
        assert len(result) == len(predicts)
        return result
    def cross_validation(self):
        """
            model cross validation check
        """
        scores = cross_val_score(MultinomialNB(alpha=0.1), self.features, self.labels, cv=2)
        logger.info(np.mean(scores))
        # scores 0.171428571429
def main():
    ocr = OCREngine()
    temp_file_name = '../base_binary.png'
    doc = ocr.recognize(temp_file_name)
    doc.dump()
    logger.info(doc.names())
    np.set_printoptions(precision=2)
    naivebayes = NaiveBayes()
    predict_data = np.array(doc.names(), ndmin=1)
    for i, v in enumerate(naivebayes.vectorizer.transform(predict_data)):
        predict = naivebayes.predict(v)[0]
        name = doc.countries[str(predict)]
        logger.info('%s -> 推定: %s', predict_data[i], name)
    out_d = naivebayes.predict_all(doc.names(), doc.countries)
    print(out_d)
    naivebayes.cross_validation()
    
    ddd = naivebayes.predict('ネッアワル王国')
    print(ddd)
if __name__ == "__main__":
    main()
