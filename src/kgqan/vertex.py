import json
from itertools import zip_longest

import requests

from kgqan.sparql_end_points import EndPoint


class Vertex:
    def __init__(self, max_num: int, candidate_uris: list, sparql_end_point: EndPoint, n_limit_EQuery: int):
        self.max_num = max_num
        self.vertices = list()
        self.predicates_uris = list()
        self.predicates_names = list()
        self.candidate_uris = candidate_uris
        self.sparql_end_point = sparql_end_point
        self.n_limit_EQuery = n_limit_EQuery

        self.process_all_vertices()

    def process_all_vertices(self):
        processed = 0
        counter = 0
        while processed < self.max_num and counter < len(self.candidate_uris):
            current_uri = self.candidate_uris[counter]
            uris, names = self.process_vertex(current_uri)
            if len(uris) == 0:
                redirected_uri = self.get_redirected_uri(current_uri)
                if redirected_uri == None:
                    self.vertices.append(current_uri)
                    self.predicates_names.append(names)
                    self.predicates_uris.append(uris)
                    processed = processed + 1
                else:
                    uris, names = self.process_vertex(redirected_uri)
                    if len(uris) != 0:
                        processed = processed + 1
                        self.vertices.append(redirected_uri)
                        self.predicates_names.append(names)
                        self.predicates_uris.append(uris)
            else:
                self.vertices.append(current_uri)
                self.predicates_names.append(names)
                self.predicates_uris.append(uris)
                processed = processed + 1
            counter = counter + 1

    def process_vertex(self, uri: str):
        uris, names = list(), list()
        URIs_false, names_false = self.sparql_end_point.get_predicates_and_their_names\
            (subj=uri, nlimit=self.n_limit_EQuery)

        URIs_true, names_true = self.sparql_end_point.get_predicates_and_their_names\
            (obj=uri, nlimit=self.n_limit_EQuery)

        if len(URIs_false) > 0 and len(URIs_true) > 0:
            URIs_false = list(zip_longest(URIs_false, [False], fillvalue=False))
            URIs_true = list(zip_longest(URIs_true, [True], fillvalue=True))
            uris.extend(URIs_false + URIs_true)
            names.extend(names_false + names_true)
        elif (len(URIs_false) > 0):
            URIs_false = list(zip_longest(URIs_false, [False], fillvalue=False))
            uris.extend(URIs_false)
            names.extend(names_false)
        elif (len(URIs_true) > 0):
            URIs_true = list(zip_longest(URIs_true, [True], fillvalue=True))
            uris.extend(URIs_true)
            names.extend(names_true)

        return uris, names

    def get_redirected_uri(self, uri):
        query = f"PREFIX dbo: <http://dbpedia.org/ontology/> select distinct ?uri where " \
                f"{{ <{uri}> dbo:wikiPageRedirects ?uri.}} "

        payload = {
            'default-graph-uri': '',
            'query': query,
            'format': 'application/json',
            'CXML_redir_for_subjs': '121',
            'CXML_redir_for_hrefs': '',
            'timeout': '30000',
            'debug': 'on',
            'run': '+Run+Query+',
        }
        query_response = requests.get("https://dbpedia.org/sparql", params=payload)
        response = json.loads(query_response.text)
        if len(response['results']['bindings']) == 0:
            return None
        return response['results']['bindings'][0]['uri']['value']

    def get_vertex_uris(self):
        return self.vertices

    # TODO Update when dealing with multiple vertices not just 1
    def get_predicates(self):
        return self.predicates_uris[0], self.predicates_names[0]






