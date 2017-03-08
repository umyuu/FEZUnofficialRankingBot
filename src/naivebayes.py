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
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import cross_val_score
from janome.tokenizer import Tokenizer
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
class CorpusTokenizer(object):
    def __init__(self, corpus):
        self.corpus = corpus
        self.t = Tokenizer()
    def read(self):
        result = []
        for word in self.corpus:
            tokens = []
            for token in self.token_split(word):
                tokens.append(token.surface)
            result.append(" ".join(tokens))
        return result
    def token_split(self, word):
        """
            filtered token　token#part_of_speech 名詞
            @param {string} word
            @return {token} token
        """
        for token in self.t.tokenize(word):
            if not str(token.part_of_speech).startswith('名詞'):
                continue
            yield token
class FeatureLabel(object):
    def __init__(self, corpus):
        pass
class NaiveBayes(object):
    """
        NaiveBayes Classifier.
        use sklearn.naive_bayes.MultinomialNB
        << preprocessing >>
            corpus => {list}words => {Word segmentation}token
        □model　training
            token => vectorizer#fit_transform => model#fit
        □predict
            token => vectorizer#transform => model#predict
    """
    def __init__(self, vectorizer=None):
        if vectorizer is None:
           vectorizer = TfidfVectorizer(use_idf=True)
        self.__vectorizer = vectorizer
        corpus = serializer.load_csv('../resource/corpus.txt')
        corpus_flat = list(itertools.chain.from_iterable(corpus))
        
        flats = []
        ct = CorpusTokenizer(corpus_flat)
        surface = ct.read()
        print(surface)
        count = CountVectorizer()
        """
            □input
              logger.info(self.vectorizer.get_feature_names())
              logger.info(self.features.toarray())
            □output
              エルソード王国, カセドリア連合王国, ゲブランド帝国, ネツァワル王国, ホルデイン王国
              [[0 0 0 1 0]
               [0 1 0 0 0]
               [0 0 1 0 0]
               [0 0 0 0 1]
               [1 0 0 0 0]]
            
            □exsample
             label:1 -> ネツァワル王国
             row:1 [0 0 0 1 0]
             cross point:1,4
        """
        
        #dim = [['ネツァワル', '王国'], ['カセドリア', '連合', '王国'], ['ゲブランド', '帝国'], ['ホルデイン', '王国'], ['エル', 'ソード', '王国']]
        #print(dim)
        self.__vectorizer = CountVectorizer(token_pattern=u'(?u)\\b\\w+\\b')
        #X = count.fit_transform(corpus_flat)
        #print(count.get_feature_names())
        #print(X.toarray())
        #self.features = self.vectorizer.fit_transform(np.array(corpus_flat, ndmin=1))
        #self.vectorizer.fit(dim)
        #self.features = self.vectorizer.transform(dim)
        self.features = self.vectorizer.fit_transform(surface)
        logger.info(self.vectorizer.get_feature_names())
        logger.info(self.features.toarray())
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
            return self.predict(v)

        logger.info(self.model.predict_proba(x))
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
            logger.info('v:%s' , str(v))
            predict = self.predict(v)[0]
            #p = self.predict(v)
            #print(p)
            result.append(pair[str(predict)])
            logger.info('%s -> 推定: %s', predict_data[i], pair[str(predict)])
        assert len(result) == len(predicts)
        #print(self.vectorizer.get_feature_names())
        return result
    def cross_validation(self):
        """
            model cross validation check
        """
        scores = cross_val_score(MultinomialNB(alpha=0.1), self.features, self.labels, cv=1)
        logger.info('cross_validation:%s', np.mean(scores))
        # scores 0.171428571429
def main():
    ocr = OCREngine()
    temp_file_name = '../base_binary.png'
    doc = ocr.recognize(temp_file_name)
    doc.dump()
    logger.info(doc.names())
    np.set_printoptions(precision=2)

    naivebayes = NaiveBayes()
    out_predict_all = naivebayes.predict_all(doc.names(), doc.countries)
    logger.info('out:%s', out_predict_all)
    #naivebayes.cross_validation()
    
    predict = naivebayes.predict('ホルデイン王国')[0]
    
    logger.info(doc.countries[str(predict)])
if __name__ == "__main__":
    main()
