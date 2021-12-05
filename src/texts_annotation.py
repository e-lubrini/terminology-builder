import spacy


class Node():
    def __init__(self, name=None):
        self.name = name
        self.points_to = dict()
        self.stored_value = None
        self.visited = False

    def point_to_node(self, other_node):
        self.points_to[other_node.name] = other_node

    def is_leaf(self):
        return self.points_to == dict()

    def is_empty(self):
        return (self.stored_value is None)

    def list_children_names(self):
        return self.points_to.keys()

    def list_children(self):
        self.points_to.values()

    def list_values_in_children(self):
        stored_values = []

        if not self.is_empty():
            stored_values.append(self.stored_value)

        if self.is_leaf():
            return stored_values

        for node in self.points_to.values():
            stored_values.extend(node.list_values_in_children())
        return stored_values


class TerminologyTree():
    def __init__(self, name="", root=Node()):
        self.name = name
        self.root = root


class Annotator:
    tagging = dict()

    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')

    def _longest_term(self, position, word_list, tree):
        current_node = tree.root
        term = []

        while True:
            try:
                word = word_list[position]
                current_node = current_node.points_to[word]
                if not current_node.is_empty():
                    aux_term = current_node.stored_value
                    if len(aux_term) > len(term):
                        term = aux_term
                position += 1
            except:
                break

        return term

    def annotate(self, tree, text):
        tagging = dict()
        position = 0
        nlp_text = self.nlp(text)
        word_list = [token.text for token in nlp_text]

        def put_tag(position, tag):
            tagging[str(position)] = tag
            return None

        while position < len(word_list):
            term = self._longest_term(position, word_list, tree)

            length = len(term)

            if length == 0:
                put_tag(position, "O")
                position += 1
            else:
                put_tag(position, "B")
                for i in range(length - 1):
                    put_tag(position + i + 1, "I")
                position += length

        text_tags = [
            (token.text, token.pos_, tagging[str(position)])
            for position, token in enumerate(nlp_text)
        ]

        return text_tags


def add_term_to_tree(term, tree):
    current_node = tree.root
    for word in term:
        if word not in current_node.points_to.keys():
            new_node = Node(word)
            current_node.points_to[word] = new_node
        else:
            new_node = current_node.points_to[word]

        current_node = new_node

    current_node.stored_value = term


def fill_terminology_tree(term_list, tree):
    for term in term_list:
        add_term_to_tree(term, tree)
    return
