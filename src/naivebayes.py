# -*- coding: utf-8 -*-
"""
    naivebayes.py
    naivebayes classifier
"""
from logging import getLogger, StreamHandler, DEBUG
#
import numpy as np
from sklearn.pipeline import Pipeline
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

class NaiveBayes(object):
    """
        NaiveBayes Classifier.
        use sklearn.naive_bayes.MultinomialNB
        << preprocessing >>
            corpus => NaiveBayes#tokenizer
            NaiveBayes#tokenizer := word => {Word segmentation}token
        □model　training
            token => vectorizer#fit_transform => model#fit
        □predict
            token => vectorizer#transform => model#predict
    """
    def __init__(self, skip_tokenize=5):
        self.skip_tokenize = skip_tokenize
        self.skip_count = 0
        self.t = Tokenizer()
        self.pipeline = Pipeline([
                ('vectorizer', TfidfVectorizer(use_idf=True, tokenizer=self.tokenizer)),
                ('classifier', MultinomialNB(0.1))])
        corpus = Serializer.load_csv('../resource/corpus.tsv')
        self.data = []
        target = []
        for row in corpus:
            self.data.append(str(row[0]))
            target.append(int(row[1]))
        self.labels = np.array(target, dtype=np.uint8, ndmin=1)
        self.pipeline.fit(self.data, self.labels)
        #logger.debug(self.vectorizer.get_feature_names())
    def tokenizer(self, word):
        """
            caller fit_transform / transform
            @param {string} word
            @yield {list.<string>}
                    result := token | space | token
        """
        if self.skip_count < self.skip_tokenize:
            self.skip_count += 1
            yield word
            return
        tokens = []
        for token in self.t.tokenize(word):
            if not str(token.part_of_speech).startswith('名詞'):
                pass
            tokens.append(token.surface)
        yield " ".join(tokens)
    @property
    def model(self):
        """
            @return {Classifier}
        """
        return self.pipeline.named_steps['classifier']
    @property
    def vectorizer(self):
        """
            @return {Vectorizer}
        """
        return self.pipeline.named_steps['vectorizer']
    def predict(self, x):
        """
            predict params x
            @param {string},{np.array} x
            @return result
        """
        if isinstance(x, str):
            x = self.vectorizer.transform([x])

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
            predicted = self.predict(x)[0]
            value = pair[str(predicted)]
            result.append(value)
            logger.debug('%s -> 推定: %s', x, value)
        assert len(result) == len(x_list)
        return result
    def cross_validation(self):
        """
            model cross validation check
        """
        #raise DeprecationWarning()
        x_train = self.vectorizer.fit_transform(self.data)
        scores = cross_val_score(self.model, x_train, self.labels, cv=5)
        logger.info('cross_validation:%s', np.mean(scores))
        # scores 0.779300699301
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
    x_list = ['ホルデイン王国', '力セドー丿ア連合王国', 'ゲブ「ラン ド帝国']
    out = naivebayes.predict_all(x_list, doc.countries)
    logger.info('out:%s', out)
    naivebayes.cross_validation()
if __name__ == "__main__":
    main()
