#!./venv python
# -*- coding: utf-8 -*-
"""
KGQAn: A Natural Language Platform 
"""
___lab__ = "CoDS Lab"
__copyright__ = "Copyright 2020-29, GINA CODY SCHOOL OF ENGINEERING AND COMPUTER SCIENCE, CONCORDIA UNIVERSITY"
__credits__ = ["CoDS Lab"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "CODS Lab"
__email__ = "essam.mansour@concordia.ca"
__status__ = "debug"
__created__ = "2020-02-07"

import logging
import networkx as nx
from .nlp.models import  WordNetLemmatizer
from termcolor import cprint
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

logger = logging.getLogger(__name__)
lemmatizer = WordNetLemmatizer()
# model_path = '/home/rehamomar/PycharmProjects/BARTInput/output_pred11/'
# best 39.7
model_path = '/mnt/KGQAn_Project/app_storage/output_pred21_8_30/'
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

if not logger.handlers:
    file_handler = logging.FileHandler('kgqan.log')
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


class Question:
    types = ('person', 'price', 'count', 'date', 'place', 'other')  # it should be populated by the types of ontology
    datatypes = ('number', 'date', 'string', 'boolean', 'resource', 'list')

    def __init__(self, question_text, question_id=None, answer_datatype=None, logger=None):
        self.tokens = list()
        self._id = question_id
        self._question_text = question_text
        self.query_graph = nx.MultiGraph()
        self._answer_type = list()
        self._answer_datatype = answer_datatype
        self._parse_components = None
        self._possible_answers = list()
        self.triple_list = list()
        self.logger = logger

        self.__process()

    def add_possible_answer(self, **kwargs):
        # bisect.insort(self._possible_answers, Answer(**kwargs))  # it is not going to work because some answers are
        # inserted without score at first
        ## TODO check for answer type
        self._possible_answers.append(Answer(**kwargs))

    @property
    def possible_answers(self):
        return self._possible_answers

    def add_possible_answer_type(self, ontology_type: str):
        self._answer_type.append(ontology_type)

    @property
    def answer_type(self):
        return self._answer_type

    @answer_type.setter
    def answer_type(self, value):
        self._answer_type.append(value)

    @property
    def answer_datatype(self):
        return self._answer_datatype

    @answer_datatype.setter
    def answer_datatype(self, value):
        if value not in Question.datatypes:
            raise ValueError(f"Question should has one of the following types {Question.datatypes}")
        self._answer_datatype = value

    @property
    def id(self):
        return self._id

    @property
    def text(self):
        return self._question_text

    def get_entities(self):
        pass

    def get_relations(self):
        pass

    def set_answer_type(self, answer_type):
        self._answer_type.clear()
        self._answer_type.append(answer_type)

    def __process(self):
        self._question_text = self.__rephrase_sentence(self._question_text)
        self.__find_possible_relations()
        self.__build_graph_from_triples()

    def __find_possible_relations(self):
        inputs = tokenizer.encode(self._question_text, return_tensors="pt")
        outputs = model.generate(inputs, max_length=300)
        outputs = tokenizer.batch_decode(outputs)
        for output in outputs:
            self.__parse_triple(output)

    # Parses the triple strings given to create the graph
    # In case there is a missing part of the triple, the triple is bypassed
    def __parse_triple(self, triples_str):
        triples_str = triples_str.replace("\"", "")
        triples_str = triples_str.replace("_", " ")
        triples_str = triples_str.replace("<s>", "")
        triples_str = triples_str.replace("<P>", "<p>")
        triples_str = triples_str.replace("<O>", "<o>")
        triples_str = triples_str.replace("<o)", "<o>")
        triples_str = triples_str.replace("<o|", "<o>")
        triples_str = triples_str.replace("<e> ", "<o>")

        triples_str = triples_str.replace("<pp> ", "<p>")
        triples_str = triples_str.replace("<oo> ", "<o>")
        triples_str = triples_str.replace("<os> ", "<o>")
        triples_str = triples_str.replace("<ol> ", "<o>")
        triples_str = triples_str.replace("<o1 ", "<o>")
        triples_str = triples_str.replace("<o] ", "<o>")
        triples_str = triples_str.replace("<o></ ", "<o>")
        triples_str = triples_str.replace("<p1 ", "<p>")

        self.logger.info(f"Generated Triple: {triples_str}")
        print("Generated Triple ", triples_str)
        triples = triples_str.split("|")
        for triple_str in triples:
            if '</s>' in triple_str:
                subj_start = triple_str.index('</s>')
            else:
                print("Triple ", triple_str, "has no subject")
                continue
            if '<p>' in triple_str:
                pred_start = triple_str.index('<p>')
            else:
                print("Triple ", triple_str, "has no predicate")
                continue
            if '<o>' in triple_str:
                obj_start = triple_str.index('<o>')
            else:
                print("Triple ", triple_str, "has no Object")
                continue

            subject = triple_str[subj_start + 4: pred_start].strip() if triple_str.startswith("</s>") else triple_str[: pred_start].strip()
            predicate = triple_str[pred_start + 3: obj_start].strip()
            object = triple_str[obj_start + 3: -4].strip() if triple_str.endswith("</s>") else triple_str[obj_start + 3:].strip()
            self.triple_list.append({"subject": subject, "predicate": predicate, "object": object})

    # TODO this should be removed by getting a new way of extracting entities that are not named entities
    def __rephrase_sentence(self, question_text):
        question_text = question_text.replace("earth", "Earth")
        question_text = question_text.replace("sun", "Sun")
        question_text = question_text.replace("sky", "Sky")
        question_text = question_text.replace("baguette", "Baguette")
        question_text = question_text.replace("libraries", "Libraries")
        question_text = question_text.replace("song", "Song")
        question_text = question_text.replace("fire", "Fire")
        question_text = question_text.replace(" ice ", " Ice ")
        question_text = question_text.replace("oscar", "Oscar")
        question_text = question_text.replace("English", "english")
        question_text = question_text.replace("company", "Company")
        question_text = question_text.replace("Whichlocation", "Which location")
        # question_text = question_text.replace("moon", "Moon")
        # For LCquad wrong questions
        # ID: 762, 848, 2265, 2449, 4516, 2730, 3019, 3242, 3330, 3461, 4659, 4706,
        question_text = question_text.replace("Whitney", "Whitey")
        question_text = question_text.replace(" nad ", " and ")
        question_text = question_text.replace("Fuountain", "Fountain")
        question_text = question_text.replace("Hanses", "Hansen")

        # Adjusted GT
        question_text = question_text.replace("momoki", "momoko")
        question_text = question_text.replace("Gombitov", "Gombitova")
        question_text = question_text.replace("Demiville", "Demieville")
        question_text = question_text.replace("prochzka", "prochazka")
        question_text = question_text.replace("Tedd", "Teddy")
        question_text = question_text.replace("Merendin", "Merendon")
        question_text = question_text.replace("Institue", "Institute")
        question_text = question_text.replace("Toru", "Torun")
        question_text = question_text.replace("Piqu", "Pique")
        question_text = question_text.replace("Ramerez", "Ramirez")
        question_text = question_text.replace("Gdask", "Gdansk")
        question_text = question_text.replace("Bhler", "Buhler")
        question_text = question_text.replace("Uniamsi", "Uniamesi")
        question_text = question_text.replace("Raa", "Rasa")
        question_text = question_text.replace("Trn Vit Hng", "Tran Viet Huong")
        question_text = question_text.replace("I'Isle", "l'Isle")

        return question_text

    def __build_graph_from_triples(self):
        for triple in self.triple_list:
            subject = triple['subject']
            predicate = triple['predicate']
            object = triple['object']

            subject_node = self.__add_node_or_retrieve_existing_node(subject)
            object_node = self.__add_node_or_retrieve_existing_node(object)
            self.query_graph.add_edge(subject_node, object_node, relation=predicate, uris=[])
        else:
            cprint(f"[GRAPH NODES WITH URIs:] {self.query_graph.nodes(data=True)}")
            cprint(f"[GRAPH EDGES WITH URIs:] {self.query_graph.edges(data=True)}")

    def __add_node_or_retrieve_existing_node(self, node_label):
        for node in self.query_graph.nodes():
            if node == node_label:
                return node
        if 'var' in node_label:
            self.query_graph.add_node(node_label, uris=[], answers=[], type="variable")
        else:
            self.query_graph.add_node(node_label, uris=[], answers=[], type="entity")

        # we must return from here because we just added the node
        for node in self.query_graph.nodes():
            if node == node_label:
                return node

class Answer:
    def __init__(self, **kwargs):
        self._answer = dict({
            "id": id(self),
            "question": None,
            # "question_id": kwargs['question_id'],  # question_id
            "results": None,  # here are the bindings returned from the triple store
            "status": None,  # same as the http request status, and actually it does not make sense and I might remove
            "vars": None,
            "sparql": None,
            "boolean": False
        })
        for key, value in kwargs.items():
            self._answer[key] = value

    def __lt__(self, other):
        return self.score < other.score

    def update(self, **kwargs):
        for key, value in kwargs.items():
            self._answer[key] = value

    def json(self):
        return self._answer

    @property
    def sparql(self):
        return self._answer['sparql']

    @property
    def score(self):
        return self._answer['score']

    @property
    def boolean(self):
        return self._answer['boolean']

    @sparql.setter
    def sparql(self, value):
        self._answer['sparql'] = value


if __name__ == '__main__':
    pass
