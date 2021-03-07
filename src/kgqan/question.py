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
from .nlp.relation import RelationLabeling
from transitions.core import MachineError
from .nlp.utils import nltk_POS_map, traverse_tree, table, punctuation
from .nlp.models import ner, elmo_ner, parser, WordNetLemmatizer
from termcolor import colored, cprint
import nltk

logger = logging.getLogger(__name__)
lemmatizer = WordNetLemmatizer()
if not logger.handlers:
    file_handler = logging.FileHandler('kgqan.log')
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


class Question:
    types = ('person', 'price', 'count', 'date')  # it should be populated by the types of ontology
    datatypes = ('number', 'date', 'string', 'boolean', 'resource', 'list')

    def __init__(self, question_text, question_id=None, answer_datatype=None):
        self.tokens = list()
        self._id = question_id
        self._question_text = question_text
        self.query_graph = nx.MultiGraph()
        self._answer_type = list()
        self._answer_datatype = answer_datatype
        self._parse_components = None
        self._possible_answers = list()

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

    def __process(self):
        self.__parse_sentence()
        self.__regroup_named_entities()
        self.__find_possible_entities_and_relations()

    def __parse_sentence(self):
        self._question_text = self.__rephrase_sentence(self._question_text)
        allannlp_ner_output = ner.predict(sentence=self._question_text)
        if not self.__check_named_entites_existance(allannlp_ner_output):
            allannlp_ner_output = elmo_ner.predict(sentence=self._question_text)

        allannlp_dep_output = parser.predict(sentence=self._question_text)

        words = allannlp_ner_output['words']
        ner_tags = allannlp_ner_output['tags']
        pos_tags = allannlp_dep_output['pos']
        dependencies = allannlp_dep_output['predicted_dependencies']
        heads = allannlp_dep_output['predicted_heads']
        # d = reformat_allennlp_ner_output(ner_tags, words)

        positions = traverse_tree(allannlp_dep_output['hierplane_tree']['root'])
        positions.sort()
        words_info = list(zip(range(1, len(words) + 1), words, heads, dependencies, positions, pos_tags, ner_tags))

        for i, w, h, d, p, pos, t in words_info:
            self.tokens.append({'index': i, 'token': w, 'head': h, 'dependency': d, 'position': p,
                                         'pos-tag': pos, 'ne-tag': t})

    def __regroup_named_entities(self):
        l2 = list()
        entity = list()
        tag = ''

        head = None
        h_d = list()
        dep = None
        poss = list()
        position = None
        for token in self.tokens:
            if token['ne-tag'].startswith('B-'):
                tag = token['ne-tag'][2:]
                position = token['position']
                if 'obj' in token['dependency'] or 'subj' in token['dependency']:
                    head, dep = token['head'], token['dependency']
                h_d.append((token['index'], token['head'], token['dependency']))
                poss.append(token['pos-tag'])
                entity.append(token['token'])
            elif token['ne-tag'].startswith('I-'):
                if 'obj' in token['dependency'] or 'subj' in token['dependency']:
                    head, dep = token['head'], token['dependency']
                h_d.append((token['index'], token['head'], token['dependency']))
                poss.append(token['pos-tag'])
                entity.append(token['token'])
            elif token['ne-tag'].startswith('L-'):
                if 'obj' in token['dependency'] or 'subj' in token['dependency']:
                    head, dep = token['head'], token['dependency']
                h_d.append((token['index'], token['head'], token['dependency']))
                entity_idxs = list(zip(*h_d))[0]
                if not head and not dep:
                    for _, _h, _d in h_d:
                        if token['head'] not in entity_idxs:
                            head, dep = _h, _d
                            break
                    else:
                        head, dep = token['head'], token['dependency']
                poss.append(token['pos-tag'])
                entity.append(token['token'])
                l2.append((token['index'], ' '.join(entity), head, dep, position, ' '.join(poss), tag))
                entity.clear()
            elif token['ne-tag'].startswith('U-'):
                l2.append((token['index'], token['token'], token['head'], token['dependency'], token['position'],
                           token['pos-tag'], token['ne-tag'][2:]))
            else:
                l2.append((token['index'], token['token'], token['head'], token['dependency'], token['position'],
                           token['pos-tag'], token['ne-tag']))
        else:
            self.tokens.clear()
            for i, w, h, d, p, pos, t in l2:
                self.tokens.append({'index': i, 'token': w, 'head': h, 'dependency': d, 'position': p, 'pos-tag': pos,
                                    'ne-tag': t})
            else:
                logger.info(f"[NAMED-ENTITIES:] {self.tokens}")

    def __find_possible_entities_and_relations(self):
        s, pred, o = list(), list(), list()
        relations_ignored = ['has', 'have', 'had', 'be', 'is', 'are', 'was', 'were', 'do', 'did', 'does',
                             'much', 'many', 'give', 'show', '']
        relation_labeling = RelationLabeling()
        # positions = [token['position'] for token in self.question.tokens]
        #  i = word index, w = word_text, h = Dep_head, d
        question_type = ""
        for token in self.tokens:
            if token['token'].lower() in ['how', 'who', 'when', 'what', 'which', 'where']:
                question_type = "wh"
                continue
            if token['token'].lower() in ['show', 'give']:
                question_type = 'list'
            if token['token'] in punctuation:
                # TODO: "they" has an indication that the answer is list of people
                continue
            if token['token'] in ['many', 'big']:
                continue
            token['token'] = token['token'].translate(table)

            try:
                pos = token["pos-tag"] if token['ne-tag'] == 'O' else 'NE'
                tok = token['token']
                eval(f'relation_labeling.{pos.replace("$", "_")}("{tok}", "{token["pos-tag"]}")')
            except AttributeError as ae:
                relation_labeling.flush_relation()
            except MachineError as me:
                print(f"MachineError: {me}")
                relation_labeling.flush_relation()
            else:
                pass
            finally:
                pass

            # if token['token'].lower() in STOPWORDS:
            #     # TODO: "they" has an indication that the answer is list of people
            #     continue

            if token['ne-tag'] != "O":
                s.append((token['index'], token['token'], token['head'], token['dependency'], token['position'], token['pos-tag'], token['ne-tag']))
            elif 'subj' in token['dependency'] or 'obj' in token['dependency']:
                self.add_possible_answer_type(token['token'])
        else:
            relation_labeling.flush_relation()
            relations = list(filter(lambda x: x.lower() not in relations_ignored, relation_labeling.relations))

        for i, entity, h, d, p, pos, t in s + o:
            # TODO: This for-loop does not consider relation between two named entities
            if entity.startswith('the '):
                entity = entity[4:]
            self.query_graph.add_node(entity, pos=pos, entity_type=t, uris=[])
            # workaround to remove be from be + verb from relations  
            for relation in relations:
                relation_key = self.query_graph.add_edge(entity, 'var', relation=relation.replace("be", ""), uris=[])

        # Apply Heuristics in case there are no nodes
        # 1) In case of WH questions, the Node is the last noun in the relation
        # 2) In case of listing question (Give all, Show all), The Node is the first noun in the relations
        if len(s + o) == 0:
            if question_type == 'wh':
                found = False
                for i in range(len(relations) - 1, -1, -1):
                    if found:
                        continue
                    for token in self.tokens:
                        if (relations[i] in token['token']) and token['pos-tag'] in ['NN', 'NNS']:
                            s.append(
                                (token['index'], relations[i], token['head'], token['dependency'], token['position'],
                                 token['pos-tag'], token['ne-tag']))
                            relations.remove(relations[i])
                            found = True
                            break
            elif question_type == 'list':
                found = False
                all_index = 0
                for i in range(len(self.tokens)):
                    if token['token'] == 'all':
                        all_index = i
                        break
                for relation in relations:
                    if found:
                        continue
                    for i in range(all_index, len(self.tokens)):
                        token = self.tokens[i]
                        if (lemmatizer.lemmatize(relation) in token['token'] or lemmatizer.lemmatize(token['token']) in relation) and token['pos-tag'] in ['NN', 'NNS']:
                            s.append(
                                (token['index'], relation.split(' ')[0], token['head'], token['dependency'], token['position'],
                                 token['pos-tag'], token['ne-tag']))
                            relations.remove(relation)
                            found = True
                            break

        logger.info(f"[NODES:] {s + o}")
        logger.info(f"[RELATIONS:] {relations}")

        cprint(colored(f"[NODES:] {s + o}"))
        cprint(colored(f"[RELATIONS:] {relations}"))


    def __check_named_entites_existance(self, ner_output) -> bool:
        for tag in ner_output['tags']:
            if tag != 'O':
                return True
        return False

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
        return question_text


class Answer:
    def __init__(self, **kwargs):
        self._answer = dict({
            "id": id(self),
            "question": None,
            # "question_id": kwargs['question_id'],  # question_id
            "results": None,  # here are the bindings returned from the triple store
            "status": None,  # same as the http request status, and actually it does not make sense and I might remove
            "vars": None,
            "sparql": None
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

    @sparql.setter
    def sparql(self, value):
        self._answer['sparql'] = value


if __name__ == '__main__':
    pass
