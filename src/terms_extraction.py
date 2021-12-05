import spacy
from spacy.matcher import Matcher


class RuleBasedExtractor:
    def __init__(self, verbose=True):
        self.nlp = spacy.load("en_core_web_sm")
        self.matcher = Matcher(self.nlp.vocab)
        self.verbose = verbose

    def extract(self, texts):
        all_terms = []
        self._add_rules()
        for num, text in enumerate(texts):
            doc = self.nlp(text)
            matches = self.matcher(doc)
            for match_id, start, end in matches:
                string_id = self.nlp.vocab.strings[match_id]
                span = doc[start:end]
                lemma = ' '.join([n.lemma_ for n in self.nlp(span.text.lower())])
                all_terms.append(lemma)

            if self.verbose:
                if num + 1 % 10 == 0:
                    # print(f'{num + 1}/{len(texts)} texts processed', end="\r")
                    print(f'{num + 1}/{len(texts)} texts processed')
        return all_terms

    def _add_rules(self):
        noun_pattern = {"POS": {"IN": ["NOUN", "PROPN"]}}
        det_pattern = {"POS": {"IN": ["DET", "PRON"]}, "OP": "?"}
        pattern = [  # [{"POS": "NOUN"}, {"POS": "NOUN"}],
            [noun_pattern, noun_pattern],
            # [{"DEP": "compound"}, {"POS": "NOUN"}],
            [noun_pattern, {"POS": "ADP"}, noun_pattern],
            [{"POS": "ADJ", "OP": "+"}, noun_pattern],
            [noun_pattern, {"POS": "ADP"}, det_pattern, noun_pattern],
            [det_pattern, {"POS": "ADJ"}, {"POS": "CCONJ"}, {"POS": "ADJ"}, noun_pattern],
        ]
        self.matcher.add("terms", pattern)
