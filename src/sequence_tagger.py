import sklearn_crfsuite

class CRFSequenceClassifier:
    def __init__(self):
        pass

    def word2features(self, sent, i):
        word = sent[i][0]
        postag = sent[i][1]

        features = {
            'bias': 1.0,
            'word.lower()': word.lower(),
            'word[-3:]': word[-3:],
            'word[-2:]': word[-2:],
            'word.isupper()': word.isupper(),
            'word.istitle()': word.istitle(),
            'word.isdigit()': word.isdigit(),
            'postag': postag,
            'postag[:2]': postag[:2],
        }
        if i > 0:
            word1 = sent[i - 1][0]
            postag1 = sent[i - 1][1]
            features.update({
                '-1:word.lower()': word1.lower(),
                '-1:word.istitle()': word1.istitle(),
                '-1:word.isupper()': word1.isupper(),
                '-1:postag': postag1,
                '-1:postag[:2]': postag1[:2],
            })
        else:
            features['BOS'] = True

        if i < len(sent) - 1:
            word1 = sent[i + 1][0]
            postag1 = sent[i + 1][1]
            features.update({
                '+1:word.lower()': word1.lower(),
                '+1:word.istitle()': word1.istitle(),
                '+1:word.isupper()': word1.isupper(),
                '+1:postag': postag1,
                '+1:postag[:2]': postag1[:2],
            })
        else:
            features['EOS'] = True

        return features

    def sent2features(self, sent):
        return [self.word2features(sent, i) for i in range(len(sent))]

    def sent2labels(self, sent):
        return [label for token, postag, label in sent]

        return [token for token, postag, label in sent]

    def convert_corpus(self, sents):
        X = [self.sent2features(s) for s in sents]
        y = [self.sent2labels(s) for s in sents]
        return X, y

    def fit(self, X_train, y_train):

        crf = sklearn_crfsuite.CRF(
            algorithm='lbfgs',
            c1=0.1,
            c2=0.1,
            max_iterations=100,
            all_possible_transitions=True)
        crf.fit(X_train, y_train)
        return crf
