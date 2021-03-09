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

import os
import re
import json
import operator
import logging
from collections import defaultdict
from itertools import count, product, zip_longest
from statistics import mean
from urllib.parse import urlparse
from gensim.parsing.preprocessing import remove_stopwords, STOPWORDS

from .sparqls import *
from .question import Question
from .nlp.utils import remove_duplicates
from . import embeddings_client as w2v, utils

import datetime
from termcolor import colored, cprint

formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

# LOGGER 1 for Info, Warning and Errors
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('kgqan.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

# LOGGER 2 for DEBUGGING
logger2 = logging.getLogger("Dos logger")
# if not logger.handlers:
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger2.addHandler(sh)
logger2.setLevel(logging.DEBUG)


class KGQAn:
    """A Natural Language Platform For Querying RDF-Based Graphs

            Usage::
            Usage::

                >>> from kgqan import KGQAn
                >>> my_kgqan = KGQAn(semantic_affinity_server='127.0.0.1:9600', n_max_answers=10)

            :param semantic_affinity_server: A string, IP and Port for the semantic similarity server of the
            form ``127.0.0.1:9600``.
            :param n_max_answers: An int, the maximum number of result items return by KGQAn.
            :rtype: A :class:`KGQAn <KGQAn>`
            """

    def __init__(self, semantic_affinity_server=None,
                n_max_answers: int = 10, n_max_Vs: int = 1, n_max_Es: int = 10, n_limit_VQuery=400, n_limit_EQuery=400):
        self._ss_server = semantic_affinity_server
        self._n_max_answers = n_max_answers  # this should affect the number of star queries to be executed against TS
        self._current_question = None
        self.n_max_Vs = n_max_Vs
        self.n_max_Es = n_max_Es
        self.n_limit_VQuery = n_limit_VQuery
        self.n_limit_EQuery = n_limit_EQuery

        cprint(f"== Execution settings : Max no. answers == {self._n_max_answers}, "
               f"Max no. Vertices == {self.n_max_Vs}, Max no. Edges == {self.n_max_Es} ")

    def ask(self, question_text: str, question_id: int = 0, answer_type: str = None,
            n_max_answers: int =None, n_max_Vs: int =None, n_max_Es: int =None):
        """KGQAn pipeline

        Usage::

            >>> from kgqan import KGQAn
            >>> my_kgqan = KGQAn()
            >>> my_kgqan.ask("What is the longest river?")


        """

        # to solve Memory Leak issue
        self.v_uri_scores = defaultdict(float)

        self.question = (question_text, question_id)
        # self.question.id = question_id

        if answer_type:
            self.question.answer_datatype = answer_type
        self._n_max_answers = n_max_answers if n_max_answers else self._n_max_answers
        self.n_max_Vs = n_max_Vs if n_max_Vs else self.n_max_Vs
        self.n_max_Es = n_max_Es if n_max_Es else self.n_max_Es
        self.detect_question_and_answer_type()
        self.rephrase_question()
        # if no named entity you should return here
        if len(self.question.query_graph) == 0:
            logger.info("[NO Named-entity or NO Relation Detected]")
            return []
        self.extract_possible_V_and_E()
        self.generate_star_queries()
        self.evaluate_star_queries()

        answers = [answer.json() for answer in self.question.possible_answers[:n_max_answers]]
        logger.info(f"\n\n\n\n{'#'*120}")
        return answers

    def detect_question_and_answer_type(self):
        # question_text = question_text.lower()
        # if question_text.startswith('Who'):
        #     question_text = re.sub('Who', 'Mohamed', question_text)

        properties = ['name', 'capital', 'country']
        # what is the name
        # what country

        if self.question.text.lower().startswith('who was'):
            self.question.answer_type = 'person'
            self.question.answer_datatype = 'resource'
            # self.question.add_entity('uri', question_type=self.question.answer_type)
        elif self.question.text.lower().startswith('who is '):
            self.question.answer_type = 'person'
            self.question.answer_datatype = 'resource'
        elif self.question.text.lower().startswith('who are '):
            self.question.answer_type = 'person'
            self.question.answer_datatype = 'list'
        elif self.question.text.lower().startswith('who '):  # Who [V]
            self.question.answer_type = 'person'
            self.question.answer_datatype = 'resource'  # of list
        elif self.question.text.lower().startswith('how many '):
            self.question.answer_type = 'count'
            self.question.answer_datatype = 'number'
        elif self.question.text.lower().startswith('how much '):
            self.question.answer_type = 'price'
            self.question.answer_datatype = 'number'
        elif self.question.text.lower().startswith('when did '):
            self.question.answer_type = 'date'
            self.question.answer_datatype = 'date'
        elif self.question.text.lower().startswith('in which '):  # In which [NNS], In which city
            self.question.answer_type = 'person'
            self.question.answer_datatype = 'resource'  # of list
        elif self.question.text.lower().startswith('which '):  # which [NNS], which actors
            self.question.answer_type = 'person'
            self.question.answer_datatype = 'list'  # of list
        elif self.question.text.lower().startswith('where '):  # where do
            self.question.answer_type = 'person'
            self.question.answer_datatype = 'resource'  # of list
        elif self.question.text.lower().startswith('show '):  # Show ... all
            self.question.answer_type = 'person'
            self.question.answer_datatype = 'list'  # of list
        else:
            pass  # 11,13,75

    def rephrase_question(self):
        if self.question.text.lower().startswith('who was'):
            pass

        # logger.info(f'[Question Reformulation (Not Impl yet):] {self.question.text},\n')

    def extract_possible_V_and_E(self):
        for entity in self.question.query_graph:
            if entity == 'uri':
                self.question.query_graph.add_node(entity, uris=[], answers=[])
                continue
            entity_query = make_keyword_unordered_search_query_with_type(entity, limit=self.n_limit_VQuery)
            cprint(f"== SPARQL Q Find V: {entity_query}")

            try:
                entity_result = json.loads(evaluate_SPARQL_query(entity_query))
            except:
                logger.error(f"Error at 'extract_possible_V_and_E' method with v_query value of {entity_query} ")
                continue

            uris, names = self.__class__.extract_resource_name(entity_result['results']['bindings'])
            scores = self.__compute_semantic_similarity_between_single_word_and_word_list(entity, names)

            URIs_with_scores = list(zip(uris, scores))
            URIs_with_scores.sort(key=operator.itemgetter(1), reverse=True)
            self.v_uri_scores.update(URIs_with_scores)
            URIs_sorted = list(zip(*URIs_with_scores))[0]
            URIs_chosen = remove_duplicates(URIs_sorted)[:self.n_max_Vs]
            self.question.query_graph.nodes[entity]['uris'].extend(URIs_chosen)

        # Find E for all relations
        for (source, destination, key, relation) in self.question.query_graph.edges(data='relation', keys=True):
            source_URIs = self.question.query_graph.nodes[source]['uris']
            destination_URIs = self.question.query_graph.nodes[destination]['uris']
            combinations = utils.get_combination_of_two_lists(source_URIs, destination_URIs, with_reversed=False)

            uris, names = list(), list()
            for comb in combinations:
                if source == 'uri' or destination == 'uri':
                    URIs_false, names_false = self._get_predicates_and_their_names(subj=comb,
                                                                                   nlimit=self.n_limit_EQuery)
                    if 'leadfigures' in names_false:
                        idx = names_false.index('leadfigures')
                        names_false[idx] = 'lead figures'
                    URIs_true, names_true = self._get_predicates_and_their_names(obj=comb, nlimit=self.n_limit_EQuery)
                else:
                    v_uri_1, v_uri_2 = comb
                    URIs_false, names_false = self._get_predicates_and_their_names(v_uri_1, v_uri_2,
                                                                                   nlimit=self.n_limit_EQuery)
                    URIs_true, names_true = self._get_predicates_and_their_names(v_uri_2, v_uri_1,
                                                                                 nlimit=self.n_limit_EQuery)
                URIs_false = list(zip_longest(URIs_false, [False], fillvalue=False))
                URIs_true = list(zip_longest(URIs_true, [True], fillvalue=True))
                uris.extend(URIs_false + URIs_true)
                names.extend(names_false + names_true)
            else:
                URIs_chosen = self.__get_chosen_URIs_for_relation(relation, uris, names)
                self.question.query_graph[source][destination][key]['uris'].extend(URIs_chosen)

        else:
            logger.info(f"[GRAPH NODES WITH URIs:] {self.question.query_graph.nodes(data=True)}")
            logger.info(f"[GRAPH EDGES WITH URIs:] {self.question.query_graph.edges(data=True)}")

    @staticmethod
    def __compute_semantic_similarity_between_single_word_and_word_list(word, word_list):
        scores = list()
        score = 0.0
        for w in word_list:
            try:
                score = w2v.n_similarity(word.lower().split(), w.lower().split())
            except KeyError:
                score = 0.0
            finally:
                scores.append(score)
        else:
            return scores

    def __get_chosen_URIs_for_relation(self, relation: str, uris: list, names: list):
        if not uris:
            return uris

        scores = self.__class__.__compute_semantic_similarity_between_single_word_and_word_list(relation, names)
        # (uri, True) ===>  (uri, True, score)
        l1, l2 = list(zip(*uris))
        URIs_with_scores = list(zip(l1, l2, scores))
        URIs_with_scores.sort(key=operator.itemgetter(2), reverse=True)
        # self.uri_scores.update(URIs_with_scores)
        return remove_duplicates(URIs_with_scores)[:self.n_max_Es]

    def generate_star_queries(self):
        possible_triples_for_all_relations = list()
        for source, destination, key, relation_uris in self.question.query_graph.edges(data='uris', keys=True):
            source_URIs = self.question.query_graph.nodes[source]['uris']
            destination_URIs = self.question.query_graph.nodes[destination]['uris']
            node_uris = source_URIs if destination == 'uri' else destination_URIs

            if len(node_uris) == 0 or len(relation_uris) == 0:
                continue
            possible_triples_for_single_relation = utils.get_combination_of_two_lists(node_uris, relation_uris)
            possible_triples_for_all_relations.append(possible_triples_for_single_relation)
        else:
            for star_query in product(*possible_triples_for_all_relations):
                score = sum([self.v_uri_scores[subj]+predicate[2] for subj, predicate in star_query])

                triple = [f'?uri <{predicate[0]}> <{v_uri}>' if predicate[1] else f'<{v_uri}> <{predicate[0]}> ?uri'
                          for v_uri, predicate in star_query]

                query = f"SELECT * WHERE {{ {' . '.join(triple)} }}"
                self.question.add_possible_answer(question=self.question.text, sparql=query, score=score)

    def evaluate_star_queries(self):
        self.question.possible_answers.sort(reverse=True)
        # for i, possible_answer in enumerate(self.question.possible_answers):
        #     print(i, possible_answer.sparql, possible_answer.score)
        qc = count(1)
        sparqls = list()
        for i, possible_answer in enumerate(self.question.possible_answers[:self._n_max_answers]):
            logger.info(f"[EVALUATING SPARQL:] {possible_answer.sparql}")
            result = evaluate_SPARQL_query(possible_answer.sparql)
            logger.info(f"[POSSIBLE SPARQLs WITH ANSWER (SORTED):] {possible_answer.sparql}")
            try:
                v_result = json.loads(result)
                result_compatiable = self.check_if_answers_type_compatiable(v_result)
                if not result_compatiable:
                    continue

                possible_answer.update(results=v_result['results'], vars=v_result['head']['vars'])
                answers = list()
                for binding in v_result['results']['bindings']:
                    answer = self.__class__.extract_resource_name_from_uri(binding['uri']['value'])[0]
                    answers.append(answer)
                else:
                    if v_result['results']['bindings']:
                        logger.info(f"[POSSIBLE ANSWER {i}:] {answers}")
                    sparqls.append(possible_answer.sparql)
            except:
                print(f" >>>>>>>>>>>>>>>>>>>> Error in binding the answers: [{result}] <<<<<<<<<<<<<<<<<<")
        else:
            self.question.sparqls = sparqls

    def check_if_answers_type_compatiable(self, result):
        if self.question.answer_datatype == 'number':
            for answer in result['results']['bindings']:
                if answer['uri']['type'] == 'typed-literal' and ('integer' in answer['uri']['datatype'] or 'usDollar' in answer['uri']['datatype']
                or 'double' in answer['uri']['datatype']):
                    return True
                else:
                    return False
        # elif 'string' in self.question.answer_datatype:
        #     for answer in result['results']['bindings']:
        #         if answer['uri']['type'] == 'typed-literal' and 'langString' in answer['uri']['datatype']:
        #             return True
        #         else:
        #             return False
        elif self.question.answer_datatype == 'date':
            for answer in result['results']['bindings']:
                if answer['uri']['type'] == 'typed-literal':
                    if 'date' in answer['uri']['datatype']:
                        return True
                    elif 'gYear' in answer['uri']['datatype']:
                        obj = datetime.datetime.strptime(answer['uri']['value'], '%Y')
                        answer['uri']['value'] = str(obj.date())
                        return True
                    else:
                        return False
                else:
                    return False
        # elif 'resource' in self.question.answer_datatype:
        #     for answer in result['results']['bindings']:
        #         if answer['uri']['type'] == 'uri' and 'resource' in answer['uri']['value']:
        #             return True
        #         else:
        #             return False
        return True

    @property
    def question(self):
        return self._current_question

    @question.setter
    def question(self, value: tuple):
        self._current_question = Question(question_text=value[0], question_id=value[1])

    @staticmethod
    def extract_resource_name(result_bindings):
        resource_names = list()
        resource_URIs = list()
        for binding in result_bindings:
            resource_URI = binding['uri']['value']
            uri_path = urlparse(resource_URI).path
            resource_name = os.path.basename(uri_path)
            dir_name = os.path.dirname(uri_path)
            if resource_name.startswith('Category:') or not dir_name.endswith('/resource'):
                continue
            resource_name = re.sub(r'(:|_|\(|\))', ' ', resource_name)
            # resource_name = re.sub(r'^Category:', '', resource_name)
            # TODO: check for URI validity
            if not resource_name.strip():
                continue
            resource_URIs.append(resource_URI)
            resource_names.append(resource_name)
        return resource_URIs, resource_names

    @staticmethod
    def extract_resource_name_from_uri(uri: str):
        resource_URI = uri
        uri_path = urlparse(resource_URI).path
        resource_name = os.path.basename(uri_path)
        resource_name = re.sub(r'(:|_|\(|\))', ' ', resource_name)
        # resource_name = re.sub(r'^Category:', '', resource_name)
        # TODO: check for URI validity
        return resource_URI, resource_name

    @staticmethod
    def extract_predicate_names(result_bindings):
        predicate_URIs = list()
        predicate_names = list()
        for binding in result_bindings:
            predicate_URI = binding['p']['value']
            uri_path = urlparse(predicate_URI).path
            predicate_name = os.path.basename(uri_path)
            p = re.compile(r'(_|\([^()]*\))')
            predicate_name = p.sub(' ', predicate_name)
            p2 = re.compile(r'([a-z0-9])([A-Z])')
            predicate_name = p2.sub(r"\1 \2", predicate_name)
            if not predicate_name.strip():
                continue
            predicate_names.append(predicate_name)
            predicate_URIs.append(predicate_URI)
        return predicate_URIs, predicate_names

    @staticmethod
    def _get_predicates_and_their_names(subj=None, obj=None, nlimit: int = 100):
        if subj and obj:
            q = sparql_query_to_get_predicates_when_subj_and_obj_are_known(subj, obj, limit=nlimit)
            uris, names = KGQAn.execute_sparql_query_and_get_uri_and_name_lists(q)
        elif subj:
            q = make_top_predicates_sbj_query(subj, limit=nlimit)
            uris, names = KGQAn.execute_sparql_query_and_get_uri_and_name_lists(q)
        elif obj:
            q = make_top_predicates_obj_query(obj, limit=nlimit)
            uris, names = KGQAn.execute_sparql_query_and_get_uri_and_name_lists(q)
        else:
            raise Exception

        escaped_names = ['22-rdf-syntax-ns', 'rdf-schema', 'owl', 'wiki Page External Link', 'wiki Page ID',
                         'wiki Page Revision ID', 'is Primary Topic Of', 'subject', 'type', 'prov', 'wiki Page Disambiguates',
                         'wiki Page Redirects', 'primary Topic', 'wiki Articles', 'hypernym', 'aliases']
        filtered_uris = []
        filtered_names = []
        for i in range(len(names)):
            if names[i] not in escaped_names:
                filtered_names.append(names[i])
                filtered_uris.append(uris[i])

        return filtered_uris, filtered_names

    @staticmethod
    def execute_sparql_query_and_get_uri_and_name_lists(q):
        cprint(f"== SPARQL Q Find E: {q}")
        result = json.loads(evaluate_SPARQL_query(q))
        return KGQAn.extract_predicate_names(result['results']['bindings'])


if __name__ == '__main__':
    my_kgqan = KGQAn()
    my_kgqan.ask(question_text='Which movies starring Brad Pitt were directed by Guy Ritchie?', n_max_answers=1)
