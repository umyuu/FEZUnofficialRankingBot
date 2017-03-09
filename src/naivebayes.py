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
from janome.tokenizer import Tokenizer
#
from serializer import Serializer
from ocrengine import OCREngine

# pylint: disable=C0103
logger = getLogger('myapp.tweetbot')
if __name__ == "__main__":
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)

class CorpusTokenizer(object):
    def __init__(self, corpus, skip_tokenize=0):
        """
            @param {list} corpus
                   {int}  skip_tokenize tokenize skiped yield result word
        """
        assert len(corpus) != 0
        self.skip_tokenize = skip_tokenize    
        self.corpus = corpus
        self.t = Tokenizer()
    def read(self):
        """
            list.<string>
                result := token | space | token
            @yield {list.<string>}
        """
        for i, word in enumerate(self.corpus):
            if i < self.skip_tokenize:
                yield word
                continue
            tokens = []
            for token in self.token_split(word):
                if not str(token.part_of_speech).startswith('名詞'):
                    pass
                tokens.append(token.surface)
            yield " ".join(tokens)
    def token_split(self, word):
        """
            tokenize iterator
            @param {string} word
            @yield {token} token
        """
        for token in self.t.tokenize(word):
            yield token
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
    def __init__(self, skip_tokenize=5):
        self.__vectorizer = TfidfVectorizer(use_idf=True)
        corpus = Serializer.load_csv('../resource/corpus.tsv')
        data = []
        target = []
        for row in corpus:
            data.append(str(row[0]))
            target.append(int(row[1]))
        self.features = self.vectorizer.fit_transform(CorpusTokenizer(data, skip_tokenize=5).read())
        self.labels = np.array(target, dtype=np.uint8, ndmin=1)
        # vectorizer debug code
        #logger.debug(self.vectorizer.get_feature_names())
        #logger.debug(self.features.toarray())
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
            v = self.vectorizer.transform(CorpusTokenizer([x]).read())
            return self.predict(v)

        logger.debug(self.model.predict_proba(x))
        return self.model.predict(x)
    def predict_all(self, x_list, pair):
        """
            mapping
            @param {list} x_list
                   {dict} pair
            @return {list} value
        """
        result = []
        for x in x_list:
            predict = self.predict(x)[0]
            value = pair[str(predict)] 
            result.append(value)
            logger.debug('%s -> 推定: %s', x, value)
        assert len(result) == len(x_list)
        return result    
    def cross_validation(self):
        """
            model cross validation check
        """
        raise DeprecationWarning()
        scores = cross_val_score(MultinomialNB(alpha=0.1), self.features, self.labels, cv=2)
        logger.info('cross_validation:%s', np.mean(scores))
        # scores 0.171428571429
def main():
    ocr = OCREngine()
    temp_file_name = '../base_binary.png'
    doc = ocr.recognize(temp_file_name)
    doc.dump()
    x_list = doc.names()
    x_list.append('エルソード')
    logger.info(x_list)
    #np.set_printoptions(precision=4)
    naivebayes = NaiveBayes()
    out = naivebayes.predict_all(x_list, doc.countries)
    logger.info('out:%s', out)
    x_list = ['ホルデイン王国','力セドー丿ア連合王国','ゲブ「ラン ド帝国']
    out = naivebayes.predict_all(x_list, doc.countries)
    logger.info('out:%s', out)
    #naivebayes.cross_validation()
if __name__ == "__main__":
    main()
