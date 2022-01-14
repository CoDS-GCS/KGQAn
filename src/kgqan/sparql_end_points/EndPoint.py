import datetime
import json
import requests
import os
import re
from urllib.parse import urlparse
from ..sparqls import *
from termcolor import cprint

class EndPoint:
    def __init__(self, knowledge_graph: str, link: str):
        self.link = link
        self.knowledge_graph = knowledge_graph

    def evaluate_SPARQL_query(self, query: str):
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
        # From public https://dbpedia.org/sparql
        # query_response = requests.get(f'https://dbpedia.org/sparql', params=payload)

        # From local http://localhost:8890/sparql
        # query_response = requests.get(f'http://localhost:8890/sparql', params=payload)

        # Moh Saleem'recommened DBpedia dataset: http://206.12.92.210:8890/sparql/
        # query_response = requests.get(f'http://206.12.92.210:8890/sparql', params=payload)

        query_response = requests.get(self.link, params=payload)
        if query_response.status_code in [414]:
            return '{"head":{"vars":[]}, "results":{"bindings": []}, "status":414 }'
        return query_response.text

    # Returns 3 objects:
    # 1) boolean indicating if the answer type is compatible with the answer)
    # 2) The result after being parsed
    # 3) boolean to indicate if we should gather the answers for logging or not, currently it is True for JSON and False for XML
    def parse_result(self, result, answer_data_type):
        v_result = json.loads(result)
        v_result, types = self.extract_types(v_result)
        result_compatiable = self.check_if_answers_type_compatible(v_result, answer_data_type)
        if not result_compatiable:
            return False, [], True, types

        return True, v_result, True, types

    def get_names_and_uris(self, entity_query):
        entity_result = json.loads(self.evaluate_SPARQL_query(entity_query))
        uris, names = self.extract_resource_name(entity_result['results']['bindings'])
        return uris, names

    def check_if_answers_type_compatible(self, result, answer_datatype):
        if not answer_datatype or not 'results' in result:
            return True

        if answer_datatype == 'number':
            return self.is_number(result)
        elif 'string' in answer_datatype:
            if self.is_number(result) or self.is_date(result):
                return False
            else:
                return True
        elif answer_datatype == 'date':
            return self.is_date(result)
        elif 'resource' in answer_datatype:
            if self.is_number(result) or self.is_date(result):
                return False
            else:
                return True
        return True

    def is_number(self, result):
        for answer in result['results']['bindings']:
            if answer['uri']['type'] == 'typed-literal' and (
                    'integer' in answer['uri']['datatype'] or 'usDollar' in answer['uri']['datatype']
                    or 'double' in answer['uri']['datatype']):
                return True
        return False

    def is_date(self, result):
        for answer in result['results']['bindings']:
            if answer['uri']['type'] == 'typed-literal':
                if 'date' in answer['uri']['datatype']:
                    return True
                elif 'gYear' in answer['uri']['datatype']:
                    if int(answer['uri']['value']) > 0:
                        obj = datetime.datetime.strptime(answer['uri']['value'], '%Y')
                        answer['uri']['value'] = str(obj.date())
                    return True
        return False

    def extract_resource_name(self, result_bindings):
        resource_names = list()
        resource_URIs = list()
        for binding in result_bindings:
            resource_name = ''
            resource_URI = binding['uri']['value']
            if self.knowledge_graph == 'dbpedia':
                resource_name, skip = self.extract_resource_name_dbpedia(binding)
                if skip:
                    continue
            else:
                resource_name = binding['label']['value']
            # resource_name = re.sub(r'^Category:', '', resource_name)
            # TODO: check for URI validity
            if not resource_name.strip():
                continue
            resource_URIs.append(resource_URI)
            resource_names.append(resource_name)
        return resource_URIs, resource_names

    def extract_resource_name_dbpedia(self, binding):
        skip = False
        resource_URI = binding['uri']['value']
        uri_path = urlparse(resource_URI).path
        resource_name = os.path.basename(uri_path)
        dir_name = os.path.dirname(uri_path)
        if resource_name.startswith('Category:') or not dir_name.endswith('/resource'):
            skip = True
        resource_name = re.sub(r'(:|_|\(|\))', ' ', resource_name)
        return resource_name, skip

    def get_predicates_and_their_names(self, subj=None, obj=None, nlimit: int = 100):
        if subj and obj:
            q = sparql_query_to_get_predicates_when_subj_and_obj_are_known(subj, obj, limit=nlimit)
            uris, names = self.execute_sparql_query_and_get_uri_and_name_lists(q)
        elif subj:
            q = make_top_predicates_sbj_query(subj, limit=nlimit)
            uris, names = self.execute_sparql_query_and_get_uri_and_name_lists(q)
        elif obj:
            q = make_top_predicates_obj_query(obj, limit=nlimit)
            uris, names = self.execute_sparql_query_and_get_uri_and_name_lists(q)
        else:
            raise Exception

        escaped_names = ['22-rdf-syntax-ns', 'rdf-schema', 'owl', 'wiki Page External Link', 'wiki Page ID',
                         'wiki Page Revision ID', 'is Primary Topic Of', 'subject', 'type', 'prov',
                         'wiki Page Disambiguates',
                         'wiki Page Redirects', 'primary Topic', 'wiki Articles', 'hypernym', 'aliases']
        filtered_uris = []
        filtered_names = []
        for i in range(len(names)):
            if names[i] not in escaped_names:
                filtered_names.append(names[i])
                filtered_uris.append(uris[i])

        return filtered_uris, filtered_names

    def execute_sparql_query_and_get_uri_and_name_lists(self, q):
        cprint(f"== SPARQL Q Find E: {q}")
        result = json.loads(self.evaluate_SPARQL_query(q))
        return self.extract_predicate_names(result['results']['bindings'])

    def extract_predicate_names(self, result_bindings):
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

    def extract_types(self, json_object):
        types = list()
        answers = list()
        current = -1
        current_types = []
        for binding in json_object['results']['bindings']:
            if not binding['uri'] in answers:
                current = current + 1
                if current != 0:
                    types.append(current_types)
                    current_types = []
                answers.append(binding['uri'])
            if 'type' in binding:
                current_types.append(binding['type']['value'])
                binding.pop('type')

        types.append(current_types)
        json_object['head']['vars'] = ['uri']
        json_object['results'].pop('bindings')
        final_binding = []
        for answer in answers:
            final_binding.append({'uri': answer})
        json_object['results']['bindings'] = final_binding

        return json_object, types


