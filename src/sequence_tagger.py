import sklearn_crfsuite
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from sklearn.metrics import classification_report
from tqdm.auto import tqdm

torch.manual_seed(1)


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


class Dataset(torch.utils.data.Dataset):
    def __init__(self, texts, word2token):
        self.texts = texts
        self.word2token = word2token
        self.tag2token = {"O": 0, "B": 1, "I": 2}

    def __getitem__(self, item):
        text = self.texts[item][0]
        labels = self.texts[item][1]
        tokens = [self.word2token.get(w, 0) for w in text]
        labels = [self.tag2token[x] for x in labels]
        return torch.tensor(tokens, dtype=torch.long), torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.texts)


class GRUTagger(nn.Module):

    def __init__(self, embedding_dim, hidden_dim, vocab_size, tagset_size):
        super(GRUTagger, self).__init__()
        self.hidden_dim = hidden_dim
        self.word_embeddings = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.GRU(embedding_dim, hidden_dim)
        self.hidden2tag = nn.Linear(hidden_dim, tagset_size)

    def forward(self, sentence):
        embeds = self.word_embeddings(sentence)
        lstm_out, _ = self.lstm(embeds.view(len(sentence), 1, -1))
        tag_space = self.hidden2tag(lstm_out.view(len(sentence), -1))
        tag_scores = F.log_softmax(tag_space, dim=1)
        return tag_scores


def train_model(model, dataloader, loss_function, optimizer, epoches=2):
    for epoch in range(epoches):
        print(f'{epoch + 1}/{epoches}')
        t = tqdm(dataloader)
        for num, (sentence, tags) in enumerate(t):
            model.zero_grad()
            tag_scores = model(sentence[0])
            loss = loss_function(tag_scores, tags[0])
            if num % 50 == 0:
                t.set_description(f"loss: {round(float(loss), 3)}")
                t.refresh()
            loss.backward()
            optimizer.step()
    return model


def convert_data(annotated_data):
    new_data = []
    for sentence in annotated_data:
        sent = []
        label = []
        for word, pos, tag in sentence:
            sent.append(word)
            label.append(tag)
            if word in ['.', '?', '!']:
                new_data.append((sent, label))
                sent = []
                label = []
    return new_data


def evaluate(model, dataloader):
    predicted = []
    true = []
    with torch.no_grad():
        t = tqdm(dataloader)
        for sentence, tags in t:
            model.zero_grad()
            tag_scores = model(sentence[0])
            pred = [torch.max(x, axis=0)[1].item() for x in tag_scores]
            predicted.extend(pred)
            true.extend(tags[0])

    print(classification_report(true, predicted))
    return predicted, true
