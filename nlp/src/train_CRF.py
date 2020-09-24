# -*- coding: utf8 -*-

import pandas as pd
# from sklearn_crfsuite import CRF
from joblib import dump
from config.config import NLPConfig

my_config = NLPConfig()
model_dir = my_config.model_path
data_dir = my_config.data_path


class SentenceGetter(object):

    def __init__(self, data):
        self.n_sent = 1
        self.data = data
        self.empty = False
        agg_func = lambda s: [(w, p, n, t) for w, p, n, t in zip(s["WORD"].values.tolist(),
                                                                 s["POS"].values.tolist(),
                                                                 s["NER"].values.tolist(),
                                                                 s["TAG"].values.tolist())]
        self.grouped = self.data.groupby("SENT#").apply(agg_func)
        self.sentences = [s for s in self.grouped]

    def get_next(self):
        try:
            s = self.grouped[self.n_sent]
            self.n_sent += 1
            return s
        except:
            print('return none!')
            return None


def word2features(sent, i):
    word = sent[i][0]
    postag = sent[i][1]
    nertag = sent[i][2]

    features = {
        'bias': 1.0,
        'word': word,
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),
        'postag': postag,
        'ner': nertag
    }

    if i > 0:
        word1 = sent[i - 1][0]
        postag1 = sent[i - 1][1]
        nertag1 = sent[i - 1][2]
        features.update({
            '-1:word': word1,
            '-1:word.isdigit()': word1.isdigit(),
            '-1:postag': postag1,
            '-1:nertag': nertag1,
        })

        if i > 1:
            word2 = sent[i - 2][0]
            postag2 = sent[i - 2][1]
            nertag2 = sent[i - 2][2]
            features.update({
                '-2:word': word2,
                '-2:postag': postag2,
                '-2:nertag': nertag2,
            })
        else:
            pass

        if i > 2:
            word3 = sent[i - 3][0]
            postag3 = sent[i - 3][1]
            nertag3 = sent[i - 3][2]
            features.update({
                '-3:word': word3,
                '-3:postag': postag3,
                '-3:nertag': nertag3,
            })
        else:
            pass

    else:
        pass

    if i < len(sent) - 1:
        word1 = sent[i + 1][0]
        postag1 = sent[i + 1][1]
        nertag1 = sent[i + 1][2]
        features.update({
            '+1:word': word1,
            '+1:postag': postag1,
            '+1:nertag': nertag1,
        })
        if i < len(sent) - 2:
            word2 = sent[i + 2][0]
            postag2 = sent[i + 2][1]
            nertag2 = sent[i + 2][2]
            features.update({
                '+2:word': word2,
                '+2:postag': postag2,
                '+2:nertag': nertag2,
            })
        else:
            pass
        if i < len(sent) - 3:
            word3 = sent[i + 3][0]
            postag3 = sent[i + 3][1]
            nertag3 = sent[i + 3][2]
            features.update({
                '+3:word': word3,
                '+3:postag': postag3,
                '+3:nertag': nertag3,
            })
        else:
            pass
    else:
        pass

    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]


def sent2labels(sent):
    return [label for token, postag, nertag, label in sent]


def sent2tokens(sent):
    return [token for token, postag, nertag, label in sent]


def train(data_file, save_to):
    df = pd.read_csv(data_file)
    df = df.fillna('O')

    getter = SentenceGetter(df)
    sentences = getter.sentesnces

    X = [sent2features(s) for s in sentences]
    y = [sent2labels(s) for s in sentences]
    crf = CRF(algorithm='lbfgs',
              c1=10,
              c2=0.1,
              max_iterations=100,
              all_possible_transitions=False)
    print('training.......')
    crf.fit(X, y)
    dump(crf, save_to)
    print('save to ' + save_to)


if __name__ == '__main__':
    train(data_dir + '102p_8764w.csv', model_dir + 'covid_ner_8764w.job')
