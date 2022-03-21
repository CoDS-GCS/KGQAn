
import logging
import operator
from itertools import chain, product, zip_longest
from termcolor import cprint

formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

# LOGGER 1 for Info, Warning and Errors
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('kgqan.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False


class linking:

    def make_keyword_unordered_search_query_with_type(keywords_string: str, limit=500):
        # for cases such as "Angela Merkel ’s"
        escape = ['’s']
        kwlist = []
        for w in keywords_string.strip().split():
            if w not in escape:
                if w.isnumeric():
                    w = '\\\'' + w + '\\\''
                    kwlist.append(w)
                else:
                    kwlist.append(w)
        kws = ' AND '.join(kwlist)
        return f"prefix rdf: <http://www.w3.org/2000/01/rdf-schema#> " \
               f"select distinct ?uri  ?label " \
               f"where {{ ?uri rdf:label ?label. ?label  <bif:contains> '{kws}' . }}  LIMIT {limit}"

    def get_combination_of_two_lists(list1, list2, directed=False, with_reversed=False):
        lists = [l for l in (list1, list2) if l]

        if len(lists) < 2:
            return set(chain(list1, list2))
        else:
            pass

        combinations = product(*lists, repeat=1)
        combinations_selected = list()
        combinations_memory = list()

        for comb in combinations:
            pair = set(comb)

            if len(lists) == 2 and len(pair) == 1:
                continue

            if not directed and pair in combinations_memory:
                continue
            combinations_memory.append(pair)
            combinations_selected.append(comb)
        else:
            if with_reversed:
                combinations_reversed = [(comb[1], comb[0]) for comb in combinations_selected if len(lists) == 2]
                combinations_selected.extend(combinations_reversed)

            return set(combinations_selected)

    def extract_possible_V_and_E(self):
        for entity in self.question.query_graph:
            if self.is_variable(entity):
                # self.question.query_graph.add_node(entity, uris=[], answers=[])
                continue
            entity_query = self.make_keyword_unordered_search_query_with_type(entity, limit=self.n_limit_VQuery)
            cprint(f"== SPARQL Q Find V: {entity_query}")

            try:
                uris, names = self.sparql_end_point.get_names_and_uris(entity_query)
            except:
                logger.error(f"Error at 'extract_possible_V_and_E' method with v_query value of {entity_query} ")
                continue

            scores = self.__compute_semantic_similarity_between_single_word_and_word_list(entity, names)

            URIs_with_scores = list(zip(uris, scores))
            URIs_with_scores.sort(key=operator.itemgetter(1), reverse=True)
            self.v_uri_scores.update(URIs_with_scores)
            URIs_sorted = []
            if len(list(zip(*URIs_with_scores))) > 0:
                URIs_sorted = list(zip(*URIs_with_scores))[0]
            # URIs_chosen = remove_duplicates(URIs_sorted)[:self.n_max_Vs]
            seen = set()
            URIs_chosen = [x for x in URIs_sorted if not (x in seen or seen.add(x))][:self.n_max_Vs]
            # if entity.lower() == 'boston tea party':
            #    URIs_chosen = ['http://dbpedia.org/resource/Boston_Tea_Party']
            self.question.query_graph.nodes[entity]['uris'].extend(URIs_chosen)

        # Find E for all relations
        for (source, destination, key, relation) in self.question.query_graph.edges(data='relation', keys=True):
            if not relation:
                continue
            source_URIs = self.question.query_graph.nodes[source]['uris']
            destination_URIs = self.question.query_graph.nodes[destination]['uris']
            combinations = self.get_combination_of_two_lists(source_URIs, destination_URIs, with_reversed=False)

            uris, names = list(), list()
            for comb in combinations:
                if self.is_variable(source) or self.is_variable(destination):
                    URIs_false, names_false = self.sparql_end_point.get_predicates_and_their_names(subj=comb,
                                                                                                   nlimit=self.n_limit_EQuery)
                    if 'leadfigures' in names_false:
                        idx = names_false.index('leadfigures')
                        names_false[idx] = 'lead figures'
                    URIs_true, names_true = self.sparql_end_point.get_predicates_and_their_names(obj=comb,
                                                                                                 nlimit=self.n_limit_EQuery)
                else:
                    URIs_false, names_false, URIs_true, names_true = [], [], [], []
                    if len(source_URIs) > 0 and len(destination_URIs) > 0:
                        v_uri_1, v_uri_2 = comb
                        URIs_false, names_false = self.sparql_end_point.get_predicates_and_their_names(v_uri_1, v_uri_2,
                                                                                                       nlimit=self.n_limit_EQuery)
                        URIs_true, names_true = self.sparql_end_point.get_predicates_and_their_names(v_uri_2, v_uri_1,
                                                                                                     nlimit=self.n_limit_EQuery)
                if len(URIs_false) > 0 and len(URIs_true) > 0:
                    URIs_false = list(zip_longest(URIs_false, [False], fillvalue=False))
                    URIs_true = list(zip_longest(URIs_true, [True], fillvalue=True))
                    uris.extend(URIs_false + URIs_true)
                    names.extend(names_false + names_true)
                elif (len(URIs_false) > 0):
                    URIs_false = list(zip_longest(URIs_false, [False], fillvalue=False))
                    uris.extend(URIs_false)
                    names.extend(names_false)
                else:
                    URIs_true = list(zip_longest(URIs_true, [True], fillvalue=True))
                    uris.extend(URIs_true)
                    names.extend(names_true)

            else:
                URIs_chosen = self.__get_chosen_URIs_for_relation(relation, uris, names)
                self.question.query_graph[source][destination][key]['uris'].extend(URIs_chosen)
        else:
            logger.info(f"[GRAPH NODES WITH URIs:] {self.question.query_graph.nodes(data=True)}")
            logger.info(f"[GRAPH EDGES WITH URIs:] {self.question.query_graph.edges(data=True)}")
