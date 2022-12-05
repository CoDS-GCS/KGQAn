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

import json
import operator
from collections import defaultdict
from itertools import count, product
from SPARQLBurger.SPARQLQueryBuilder import *

from kgqan.vertex import Vertex
from .sparql_end_points.EndPoint import EndPoint
from .sparql_end_points.XML_EndPoint import XML_EndPoint

from .sparqls import *
from .question import Question
from .nlp.utils import remove_duplicates
from .nlp.models import cons_parser, WordNetLemmatizer

import time
from .filteration import *
from termcolor import  cprint
import networkx as nx


formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

# LOGGER 1 for Info, Warning and Errors
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('kgqan.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False

# LOGGER 2 for DEBUGGING
logger2 = logging.getLogger("Dos logger")
# if not logger.handlers:
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger2.addHandler(sh)
logger2.setLevel(logging.DEBUG)
logger2.propagate = False

# TODO check best place to have these updates and send either uri or key according to usecase

knowledge_graph_to_uri = {"dbpedia": "http://206.12.95.86:8890/sparql",
                          "lc_quad": "http://206.12.95.86:8891/sparql",
                          "microsoft_academic": "https://makg.org/sparql",
                          "open_citations": "https://opencitations.net/sparql",
                          "yago": "http://206.12.95.86:8892/sparql",
                          "fact_forge": "http://factforge.net/sparql",
                          "bgee": "https://bgee.org/sparql",
                          "dblp": "http://206.12.95.86:8894/sparql"}


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
                 n_max_answers: int = 10, n_max_Vs: int = 1, n_max_Es: int = 10, n_limit_VQuery=400,
                 n_limit_EQuery=400):
        self.target_variable = None
        self._ss_server = semantic_affinity_server
        self._n_max_answers = n_max_answers  # this should affect the number of star queries to be executed against TS
        self._current_question = None
        self.n_max_Vs = n_max_Vs
        self.n_max_Es = n_max_Es
        self.n_limit_VQuery = n_limit_VQuery
        self.n_limit_EQuery = n_limit_EQuery
        self.knowledge_graph = ''
        self.sparql_end_point = None
        self.lemmatizer = WordNetLemmatizer()
        self.connected_predicates = 0

        cprint(f"== Execution settings : Max no. answers == {self._n_max_answers}, "
               f"Max no. Vertices == {self.n_max_Vs}, Max no. Edges == {self.n_max_Es} ")

    def ask(self, question_text: str, knowledge_graph, question_id: int = 0, answer_type: str = None,
            n_max_answers: int = None, n_max_Vs: int = None, n_max_Es: int = None):
        """KGQAn pipeline

        Usage::

            >>> from kgqan import KGQAn
            >>> my_kgqan = KGQAn()
            >>> my_kgqan.ask("What is the longest river?")


        """

        # to solve Memory Leak issue
        self.v_uri_scores = defaultdict(float)
        logger.info(f"Question: {question_text}")
        understanding_start = time.time()
        self.question = (question_text, question_id, logger)
        understanding_end = time.time()
        # self.question.id = question_id
        self.knowledge_graph = knowledge_graph
        if answer_type:
            self.question.answer_datatype = answer_type
        self._n_max_answers = n_max_answers if n_max_answers else self._n_max_answers
        self.n_max_Vs = n_max_Vs if n_max_Vs else self.n_max_Vs
        self.n_max_Es = n_max_Es if n_max_Es else self.n_max_Es
        if knowledge_graph in ['open_citations']:
            self.sparql_end_point = XML_EndPoint(knowledge_graph, knowledge_graph_to_uri[knowledge_graph])
        else:
            self.sparql_end_point = EndPoint(knowledge_graph, knowledge_graph_to_uri[knowledge_graph])

        self.detect_question_and_answer_type()
        # if no named entity you should return here
        if len(self.question.query_graph) == 0:
            logger.info("[NO Named-entity or NO Relation Detected]")
            return [], [], [], understanding_end - understanding_start, 0, 0
        linking_start = time.time()
        self.extract_possible_V_and_E()
        linking_end = time.time()
        execution_start = time.time()
        self.generate_queries_new()
        # self.generate_star_queries()
        self.evaluate_star_queries()

        answers = [answer.json() for answer in self.question.possible_answers[:n_max_answers]]
        execution_end = time.time()
        logger.info(f"\n\n\n\n{'#' * 120}")
        return answers, self.question.query_graph.nodes, self.question.query_graph.edges, understanding_end - understanding_start, linking_end - linking_start, execution_end - execution_start

    def detect_question_and_answer_type(self):
        properties = ['name', 'capital', 'country']
        # what is the name
        # what country
        #TODO revise
        if not self.question.answer_datatype:
            self.question.answer_type = 'string'
            self.question.answer_datatype = 'string'

        if self.question.text.lower().startswith('who was'):
            self.question.answer_type = 'person'
            self.question.answer_datatype = 'resource'
        elif self.question.text.lower().startswith('who is '):
            self.question.answer_type = 'person'
            self.question.answer_datatype = 'resource'
        elif self.question.text.lower().startswith('are '):
            self.question.answer_type = 'boolean'
            self.question.answer_datatype = 'boolean'
        elif self.question.text.lower().startswith('is '):
            self.question.answer_type = 'boolean'
            self.question.answer_datatype = 'boolean'
        elif self.question.text.lower().startswith('did '):
            self.question.answer_type = 'boolean'
            self.question.answer_datatype = 'boolean'
        elif self.question.text.lower().startswith('do '):
            self.question.answer_type = 'boolean'
            self.question.answer_datatype = 'boolean'
        elif self.question.text.lower().startswith('does '):
            self.question.answer_type = 'boolean'
            self.question.answer_datatype = 'boolean'
        elif self.question.text.lower().startswith('who are '):
            self.question.answer_type = 'person'
            self.question.answer_datatype = 'list'
        elif self.question.text.lower().startswith('who '):  # Who [V]
            self.question.answer_type = 'person'
            self.question.answer_datatype = 'resource'  # of list
        elif self.question.text.lower().startswith('whom '):  # Who [V]
            self.question.answer_type = 'person'
            self.question.answer_datatype = 'resource'  # of list
        elif self.question.text.lower().startswith('how many '):
            self.question.answer_type = 'count'
            self.question.answer_datatype = 'number'
        elif self.question.text.lower().startswith('how much '):
            self.question.answer_type = 'price'
            self.question.answer_datatype = 'number'
        elif self.question.text.lower().startswith('when did ') or self.question.text.lower().startswith('when was '):
            self.question.answer_type = 'date'
            self.question.answer_datatype = 'date'
        elif self.question.text.lower().startswith('when '):
            self.question.answer_type = 'date'
            self.question.answer_datatype = 'date'
        # TODO Start workarouds
        elif self.question.text.lower().startswith('which airports '):  # where do
            self.question.answer_type = 'place'
            self.question.answer_datatype = 'resource'  # of list
        elif self.question.text.lower().startswith('which languages '):  # where do
            self.question.answer_type = 'language'
            self.question.answer_datatype = 'resource'  # of list
        elif self.question.text.lower().startswith('what languages '):  # where do
            self.question.answer_type = 'language'
            self.question.answer_datatype = 'resource'  # of list
        elif self.question.text.lower().startswith('which countries '):  # where do
            self.question.answer_type = 'place'
            self.question.answer_datatype = 'resource'  # of list
        # TODO End workarouds
        elif self.question.text.lower().startswith('in which '):  # In which [NNS], In which city
            self.question.answer_type = 'place'
            self.question.answer_datatype = 'resource'  # of list
        elif self.question.text.lower().startswith('which '):  # which [NNS], which actors
            self.question.answer_type = 'other'
            self.question.answer_datatype = 'list'  # of list
        elif self.question.text.lower().startswith('where '):  # where do
            self.question.answer_type = 'place'
            self.question.answer_datatype = 'resource'  # of list
        elif self.question.text.lower().startswith('show '):  # Show ... all
            self.question.answer_type = 'other'
            self.question.answer_datatype = 'list'  # of list
        else:
            pass  # 11,13,75

        # Which Trial
        if self.question.text.lower().startswith('which ') or self.question.text.lower().startswith(' in which '):
            allennlp_dep_output = cons_parser.predict(sentence=self.question.text)
            for tag in zip(allennlp_dep_output['pos_tags'], allennlp_dep_output['tokens']):
                if tag[0] in ['NN', 'NNS']:
                    self.question.set_answer_type(self.lemmatizer.lemmatize(tag[1]))
                    break
        if self.knowledge_graph == "lc_quad" or self.knowledge_graph == "dblp" or self.knowledge_graph == "microsoft_academic":
            if self.question.text.lower().startswith('to which ') or self.question.text.lower().startswith('under which ')\
                or self.question.text.lower().startswith('what ') or self.question.text.lower().startswith('give ')\
                or self.question.text.lower().startswith('name ') or self.question.text.lower().startswith('list '):
                allennlp_dep_output = cons_parser.predict(sentence=self.question.text)
                for tag in zip(allennlp_dep_output['pos_tags'], allennlp_dep_output['tokens']):
                    if tag[0] in ['NN', 'NNS']:
                        self.question.set_answer_type(self.lemmatizer.lemmatize(tag[1]))
                        break


    def update_connected_predicate_count(self, uri):
        count_response = self.sparql_end_point.evaluate_SPARQL_query(get_connected_predicate(uri))
        response_json = json.loads(count_response)
        count = response_json['results']['bindings'][0]["p_count"]["value"]
        return count

    def extract_possible_V_and_E(self):
        for entity in self.question.query_graph:
            if self.is_variable(entity):
                # self.question.query_graph.add_node(entity, uris=[], answers=[])
                continue
            if self.knowledge_graph in ['microsoft_academic', 'bgee']:
                entity_query = make_Ms_academic_query(entity, limit=self.n_limit_VQuery)
            else:
                entity_query = make_keyword_unordered_search_query_with_type(entity, limit=self.n_limit_VQuery)
            #entity_query = make_keyword_unordered_search_query_with_type(entity, limit=self.n_limit_VQuery)
            cprint(f"== SPARQL Q Find V: {entity_query}")

            try:
                uris, names = self.sparql_end_point.get_names_and_uris(entity_query)
            except:
                logger.error(f"Error at 'extract_possible_V_and_E' method with v_query value of {entity_query} ")
                continue

            scores = self.__compute_semantic_similarity_between_single_word_and_word_list(entity, names)

            URIs_with_scores = list(zip(uris, scores))
            URIs_with_scores.sort(key=operator.itemgetter(1), reverse=True)
            # print("Vertex with scores")
            # print(URIs_with_scores)
            self.v_uri_scores.update(URIs_with_scores)
            URIs_sorted = []
            if len(list(zip(*URIs_with_scores))) > 0:
                URIs_sorted = list(zip(*URIs_with_scores))[0]
            updated_vertex = Vertex(self.n_max_Vs, URIs_sorted, self.sparql_end_point, self.n_limit_EQuery)
            URIs_chosen = updated_vertex.get_vertex_uris()
            # URIs_chosen = remove_duplicates(URIs_sorted)[:self.n_max_Vs]
            self.question.query_graph.nodes[entity]['uris'].extend(URIs_chosen)
            self.question.query_graph.nodes[entity]['vertex'] = updated_vertex

        # Find E for all relations
        for (source, destination, key, relation) in self.question.query_graph.edges(data='relation', keys=True):
            if not relation:
                continue
            source_URIs = self.question.query_graph.nodes[source]['uris']
            destination_URIs = self.question.query_graph.nodes[destination]['uris']
            uris, names = list(), list()
            if not self.is_variable(source):
                for source_uri in source_URIs:
                    #TODO what if source is associated with multiple vertices
                    uris_source, names_source = self.question.query_graph.nodes[source]['vertex'].get_predicates()
                    uris.extend(uris_source)
                    names.extend(names_source)

            if not self.is_variable(destination):
                for destination_uri in destination_URIs:
                    #TODO what if source is associated with multiple vertices
                    uris_destination, names_destination = self.question.query_graph.nodes[destination]['vertex']\
                        .get_predicates()
                    uris.extend(uris_destination)
                    names.extend(names_destination)

            URIs_chosen = self.__get_chosen_URIs_for_relation(relation, uris, names)
            # print("Edges CHosen")
            # print(URIs_chosen)
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
        # (uri, vetrex, True) ===>  (uri, vertex, True, score)
        l1, l2, l3 = list(zip(*uris))
        URIs_with_scores = list(zip(l1, l2, l3, scores))
        URIs_with_scores.sort(key=operator.itemgetter(3), reverse=True)
        # print("Edges with scores")
        return remove_duplicates(URIs_with_scores)[:self.n_max_Es]

    def generate_queries_new(self):
        possible_triples_for_all_relations = list()
        for source, destination, key, edge_info in self.question.query_graph.edges(data="uris", keys=True):
            source_URIs = self.question.query_graph.nodes[source]['uris']
            destination_URIs = self.question.query_graph.nodes[destination]['uris']
            node1_uris = ["?" + source] if self.is_variable(source) else source_URIs
            node2_uris = ["?" + destination] if self.is_variable(destination) else destination_URIs
            possible_triples = self.get_all_possible_triples_for_edge(edge_info, node1_uris, node2_uris)
            self.question.query_graph[source][destination][key]['possible_triples'] = possible_triples
            if len(possible_triples) > 0:
                possible_triples_for_all_relations.append(possible_triples)
            # print(source)
            # print(source_URIs)
            # print(destination)
            # print(destination_URIs)
            # print(edge_info)
        if not self.check_validity(possible_triples_for_all_relations):
            return
        possible_bgps = self.get_possible_combinations()
        for bgp in possible_bgps:
            # print(bgp)
            score = self.calculate_score(bgp)
            if len(bgp) == 0:
                continue

            query, _, _ = self.generate_sparql_query_new(bgp)
            query = query.replace("\n", " ")
            # print(query)
            # self.question.add_possible_answer(question=self.question.text, sparql=query, score=score,
            #                                   node1=node1_uris, node2=node2_uris, edges=relation_uris)
            self.question.add_possible_answer(question=self.question.text, sparql=query, score=score)
        # for star_query in product(*possible_triples_for_all_relations):
        #     score = self.calculate_score(star_query)
        #     if len(star_query) == 0:
        #         continue
        #
        #     query, _, _ = self.generate_sparql_query_new(star_query)
        #     query = query.replace("\n", " ")
        #     # print(query)
        #     # self.question.add_possible_answer(question=self.question.text, sparql=query, score=score,
        #     #                                   node1=node1_uris, node2=node2_uris, edges=relation_uris)
        #     self.question.add_possible_answer(question=self.question.text, sparql=query, score=score)
        #
    def get_possible_combinations(self):
        edges = list(nx.dfs_edges(self.question.query_graph))
        bgps = []
        handled_edges = 0
        # if len(edges) == 1:
        #     bgps = list(product(self.question.query_graph[edges[0][0]][edges[0][1]][0]['possible_triples']))
        # elif len(edges) > 0:
        if len(edges) > 0:
            bgps = self.question.query_graph[edges[0][0]][edges[0][1]][0]['possible_triples']
            handled_edges += 1
        for i in range(1, len(edges)):
            connected_node = set(edges[i]).intersection(set(edges[i-1]))
            if len(connected_node) == 0:
                continue
            connected_node = next(iter(connected_node))
            current_triples = self.question.query_graph[edges[i][0]][edges[i][1]][0]['possible_triples']
            # print(connected_node)
            if self.is_variable(connected_node):
                bgps = product(bgps, current_triples)
            else:
                connected_node_vertices = self.question.query_graph.nodes[connected_node]['uris']
                updated_bgps = []
                for triple in current_triples:
                    used_vertex_triple = triple[0] if triple[0] in connected_node_vertices else triple[2]
                    for bgp in bgps:
                        last_bgp_triple = bgp[len(bgp) - 1]
                        used_bgp_vertex = last_bgp_triple[0] if last_bgp_triple[0] in connected_node_vertices \
                            else last_bgp_triple[2]
                        if used_vertex_triple == used_bgp_vertex:
                            temp = bgp.append(triple)
                            updated_bgps.append(temp)
                bgps = updated_bgps
            handled_edges += 1

        if handled_edges == 1:
            bgps = list(product(bgps))
        # print(len(bgps))
        return bgps

    def check_validity(self, triples):
        if len(triples) == 1 and len(triples[0]) == 2 and self.is_variable(triples[0][0][0]) and \
                self.is_variable(triples[0][0][2]) and self.is_variable(triples[0][1][0]) and\
                self.is_variable(triples[0][1][2]):
            print("In condition")
            return False
        return True
    def generate_star_queries(self):
        possible_triples_for_all_relations = list()
        for source, destination, key, relation_uris in self.question.query_graph.edges(data='uris', keys=True):
            source_URIs = self.question.query_graph.nodes[source]['uris']
            destination_URIs = self.question.query_graph.nodes[destination]['uris']
            if(self.is_variable(source) or self.is_variable(destination)):
                node_uris = source_URIs if self.is_variable(destination) else destination_URIs
                if len(node_uris) == 0 or len(relation_uris) == 0:
                    continue
                possible_triples_for_single_relation = utils.get_combination_of_two_lists(node_uris, relation_uris)
                # print(possible_triples_for_single_relation)
                possible_triples_for_all_relations.append(possible_triples_for_single_relation)
            elif len(source_URIs) > 0 and len(destination_URIs) > 0:
                possible_triples_for_ask_query = utils.get_combination_of_three_lists(source_URIs, destination_URIs, relation_uris)
                possible_triples_for_all_relations.append(possible_triples_for_ask_query)
                # for star_query in possible_triples_for_ask_query:
                #     query = self.generate_ask_sparql_query(star_query)
        else:
            for star_query in product(*possible_triples_for_all_relations):
                score = self.calculate_score(star_query)
                if len(star_query) == 0:
                    continue

                if len(star_query[0]) == 2:

                    # score = sum([self.v_uri_scores[subj] + predicate[2] for subj, predicate in star_query])
                    # score = self.calculate_score(star_query)
                    # print("current score = ", score, " new score = ", self.calculate_score(star_query))
                    # TODO update the calculation for mapping between different nodes and uris
                    query, node_uris, relation_uris = self.generate_sparql_query(star_query)
                    query = query.replace("\n", " ")
                    # print(query.replace("\n", " "))
                    # triple = []
                    # node_uris = []
                    # relation_uris = []
                    # for v_uri, predicate in star_query:
                    #     triple.append(
                    #         f'?uri <{predicate[0]}> <{v_uri}>' if predicate[1] else f'<{v_uri}> <{predicate[0]}> ?uri')
                    #     node_uris.append(v_uri)
                    #     relation_uris.append(predicate[0])
                    #
                    # query = f"SELECT * WHERE {{ {' . '.join(triple)} }}"
                    # print("Correct")
                    # print(query)
                    self.question.add_possible_answer(question=self.question.text, sparql=query, score=score,
                                                      nodes=node_uris, edges=relation_uris)
                elif len(star_query[0]) == 3:
                    # score = self.calculate_score(star_query)
                    query, node1_uris, node2_uris, relation_uris = self.generate_ask_sparql_query(star_query)
                    query = query.replace("\n", " ")
                    self.question.add_possible_answer(question=self.question.text, sparql=query, score=score,
                                                      node1=node1_uris, node2=node2_uris, edges=relation_uris)
                else:
                    print("Error dealing with query, ", star_query)

    def calculate_score(self, star_query):
        score = 0.0
        score_count = 0
        for q in star_query:
            if len(q) == 2:
                score += self.v_uri_scores[q[0]]
                score += q[1][2]
                score_count += 2
            elif len(q) == 3:
                if not self.is_variable(q[0]):
                    score += self.v_uri_scores[q[0]]
                    score_count += 1
                score += q[1][1]
                score_count += 1
                if not self.is_variable(q[2]):
                    score += self.v_uri_scores[q[2]]
                    score_count += 1
        return score / score_count if score_count > 0 else score

    # Edge is an array of (predicate, vertex, orientation, score), orientation = false -> vertex is subject,
    # True-> vertex is object
    # first_uris are the nodes of the first connected vertex to the edge
    # second_uris are the nodes of the second connected vertex to the edge
    # They should be in a format of (uri, score)
    # Assumptions:
    # 1) edges are sent in the required format
    # 2) for variables nodes, the uris will contain var1, or any information should be sent to add this information to
    # this method so the triples are ready and complete
    # Points to consider
    # 1) What if any of the node_uris or the edge uris are empty.
    # 2) What If the edge is between two variables, then it won't be annotated with any relation
    def get_all_possible_triples_for_edge(self, edge, first_uris, second_uris):
        possible_triples = list()
        for predicate, vertex, orientation, score in edge:
            if orientation:
                # vertex is object
                object_uris = [vertex]
                if vertex in first_uris:
                    subject_uris = second_uris
                elif vertex in second_uris:
                    subject_uris = first_uris
            else:
                # vertex is subject
                subject_uris = [vertex]
                if vertex in first_uris:
                    object_uris = second_uris
                elif vertex in second_uris:
                    object_uris = first_uris
            triples = list(product(subject_uris, [(predicate, score)], object_uris))
            possible_triples.extend(triples)

        # This means that we have a triple of this structure (var1 ?p var2)
        if len(edge) == 0 and len(first_uris) > 0 and len(second_uris) and self.is_variable(first_uris[0]) and\
                self.is_variable(second_uris[0]):
            possible_triples.append((first_uris[0], ('?p', 0), second_uris[0]))
            possible_triples.append((second_uris[0], ('?p', 0), first_uris[0]))

        return possible_triples

    def generate_ask_sparql_query(self, triple):
        ask_triple = []
        node1_uris = []
        node2_uris = []
        relation_uris = []
        for n1_uri, predicate, n2_uri in triple:
            if predicate[1]:
                ask_triple.append(f'<{n2_uri}> <{predicate[0]}> <{n1_uri}>')
            else:
                ask_triple.append(f'<{n1_uri}> <{predicate[0]}> <{n2_uri}>')
            node1_uris.append(n1_uri)
            node2_uris.append(n2_uri)
            relation_uris.append(predicate[0])
        query = f"ASK {{ {' . '.join(ask_triple)} }}"
        # ask_query, node1_uris,node2_uris, relation_uris = self.generate_sparql_query(query)
        # ask_query = query.replace("\n", " ")
        return query, node1_uris, node2_uris, relation_uris

    # TODO add node and vertices uris for the website, update boolean part in a better way

    def generate_sparql_query_new(self, star_query):
        if self.question.answer_datatype == 'boolean':
            ask_triple = []
            node1_uris = []
            node2_uris = []
            relation_uris = []
            for n1_uri, predicate, n2_uri in star_query:
                if predicate[1]:
                    ask_triple.append(f'<{n2_uri}> <{predicate[0]}> <{n1_uri}>')
                else:
                    ask_triple.append(f'<{n1_uri}> <{predicate[0]}> <{n2_uri}>')
                node1_uris.append(n1_uri)
                node2_uris.append(n2_uri)
                relation_uris.append(predicate[0])
            query = f"ASK {{ {' . '.join(ask_triple)} }}"
            # ask_query, node1_uris,node2_uris, relation_uris = self.generate_sparql_query(query)
            # ask_query = query.replace("\n", " ")
            # return query, node1_uris, node2_uris, relation_uris
            return query, node1_uris, node2_uris
        else:
            select_query = SPARQLSelectQuery()
            where_pattern = SPARQLGraphPattern()
            node_uris = []
            relation_uris = []
            candidate_targets = []
            for n1_uri, predicate, n2_uri in star_query:
                if self.is_variable(n1_uri):
                    uri1 = n1_uri
                    candidate_targets.append(uri1)
                else:
                    uri1 = f'<{n1_uri}>'

                if self.is_variable(n2_uri):
                    uri2 = n2_uri
                    candidate_targets.append(uri2)
                else:
                    uri2 = f'<{n2_uri}>'

                p = predicate[0] if predicate[0] == '?p' else f'<{predicate[0]}>'
                # uri2 = n2_uri if self.is_variable(n2_uri) else f'<{n2_uri}>'
                where_pattern.add_triples(
                    triples=[Triple(subject=uri1, predicate=p, object=uri2)])

            candidate_targets.sort()
            self.target_variable = candidate_targets[0] if len(candidate_targets) > 0 else "?var1"
            select_query.add_variables(variables=[self.target_variable, "?type"])
            # remove the question mark for further use
            self.target_variable = self.target_variable[1:]
            optional_pattern = SPARQLGraphPattern(optional=True)
            optional_pattern.add_triples(
                triples=[
                    Triple(subject='?var1', predicate='<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>',
                           object='?type')
                ]
            )
            where_pattern.add_nested_graph_pattern(optional_pattern)
            select_query.set_where_pattern(graph_pattern=where_pattern)
            return select_query.get_text(), node_uris, relation_uris
    #TODO update with 2 variables
    def generate_sparql_query(self, star_query):
        select_query = SPARQLSelectQuery()
        #select_query.add_variables(variables=["?uri"])
        select_query.add_variables(variables=["?uri", "?type"])
        where_pattern = SPARQLGraphPattern()
        node_uris = []
        relation_uris = []

        for v_uri, predicate in star_query:
            if predicate[1]:
                where_pattern.add_triples(triples=[Triple(subject='?uri', predicate=f'<{predicate[0]}>', object=f'<{v_uri}>')])
            else:
                where_pattern.add_triples(triples=[Triple(subject=f'<{v_uri}>', predicate=f'<{predicate[0]}>', object='?uri')])
            node_uris.append(v_uri)
            relation_uris.append(predicate[0])

        optional_pattern = SPARQLGraphPattern(optional=True)
        optional_pattern.add_triples(
            triples=[
                Triple(subject='?uri', predicate='<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>', object='?type')
            ]
        )
        where_pattern.add_nested_graph_pattern(optional_pattern)
        select_query.set_where_pattern(graph_pattern=where_pattern)
        return select_query.get_text(), node_uris, relation_uris

    def evaluate_star_queries(self):
        self.question.possible_answers.sort(reverse=True)
        qc = count(1)
        sparqls = list()
        for i, possible_answer in enumerate(self.question.possible_answers[:self._n_max_answers]):
            logger.info(f"[EVALUATING SPARQL:] {possible_answer.sparql}")
            result = self.sparql_end_point.evaluate_SPARQL_query(possible_answer.sparql)
            logger.info(f"[POSSIBLE SPARQLs WITH ANSWER (SORTED):] {possible_answer.sparql}")
            try:
                result_compatible, v_result, get_answers, types= self.sparql_end_point.parse_result\
                    (result, self.question.answer_datatype, self.target_variable)
                if not result_compatible:
                    continue
                # The else is for boolean questions
                if 'results' in v_result:
                    filtered_results = update_results(v_result['results'], self.question.answer_type, types, self.knowledge_graph)
                    possible_answer.update(results=filtered_results, vars=v_result['head']['vars'])
                else:
                    possible_answer.update(results=[], boolean=v_result['boolean'])
                sparqls.append(possible_answer.sparql)

                if get_answers:
                    answers = list()
                    if 'results' in v_result:
                        for binding in v_result['results']['bindings']:
                            answer = self.__class__.extract_resource_name_from_uri(binding['uri']['value'])[0]
                            answers.append(answer)
                        else:
                            if v_result['results']['bindings']:
                                logger.info(f"[POSSIBLE ANSWER {i}:] {answers}")
                    else:
                        answers.append(v_result['boolean'])
                # print(possible_answer.sparql)
            except Exception as e:
                #traceback.print_exc()
                print(f" >>>>>>>>>>>>>>>>>>>> Error in binding the answers: [{result}] <<<<<<<<<<<<<<<<<<")
        else:
            self.question.sparqls = sparqls

    def is_variable(self, label):
        return 'var' in label

    @property
    def question(self):
        return self._current_question

    @question.setter
    def question(self, value: tuple):
        self._current_question = Question(question_text=value[0], question_id=value[1], logger=value[2])

    @staticmethod
    def extract_resource_name_dbpedia(binding):
        skip = False
        resource_URI = binding['uri']['value']
        uri_path = urlparse(resource_URI).path
        resource_name = os.path.basename(uri_path)
        dir_name = os.path.dirname(uri_path)
        if resource_name.startswith('Category:') or not dir_name.endswith('/resource'):
            skip = True
        resource_name = re.sub(r'(:|_|\(|\))', ' ', resource_name)
        return resource_name, skip

    @staticmethod
    def extract_resource_name(result_bindings, knowledge_graph):
        resource_names = list()
        resource_URIs = list()
        for binding in result_bindings:
            resource_name = ''
            resource_URI = binding['uri']['value']
            if knowledge_graph == 'dbpedia':
                resource_name, skip = KGQAn.extract_resource_name_dbpedia(binding)
                if skip:
                    continue
            elif knowledge_graph == 'microsoft_academic':
                resource_name = binding['label']['value']
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
        # TODO: check for URI validity
        return resource_URI, resource_name


if __name__ == '__main__':
    my_kgqan = KGQAn()
    my_kgqan.ask(question_text='Which movies starring Brad Pitt were directed by Guy Ritchie?', n_max_answers=1)
