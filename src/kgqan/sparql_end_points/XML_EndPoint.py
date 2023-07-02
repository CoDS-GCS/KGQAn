import traceback

from .EndPoint import EndPoint
import requests
import xml.etree.ElementTree as ET
from termcolor import cprint


class XML_EndPoint(EndPoint):
    def evaluate_SPARQL_query(self, query: str):
        payload = {
            # 'default-graph-uri': '',
            "query": query,
            "format": "application/rdf+xml",
            # 'CXML_redir_for_subjs': '121',
            # 'CXML_redir_for_hrefs': '',
            # 'timeout': '30000',
            # 'debug': 'on',
            # 'run': '+Run+Query+',
        }
        query_response = requests.get(self.link, params=payload)
        if query_response.status_code in [414]:
            return '{"head":{"vars":[]}, "results":{"bindings": []}, "status":414 }'
        return query_response.text

    def parse_result(self, result, answer_data_type):
        try:
            root = ET.fromstring(result)
            result_uri = root.findall(
                ".//{http://www.w3.org/2005/sparql-results#}results/{http://www.w3.org/2005/sparql-results#}result/{http://www.w3.org/2005/sparql-results#}binding/{http://www.w3.org/2005/sparql-results#}uri"
            )
            result_literal = root.findall(
                ".//{http://www.w3.org/2005/sparql-results#}results/{http://www.w3.org/2005/sparql-results#}result/{http://www.w3.org/2005/sparql-results#}binding/{http://www.w3.org/2005/sparql-results#}literal"
            )
            bindings = []
            for r in result_uri + result_literal:
                el = {"uri": {"type": "uri", "value": r.text}}
                bindings.append(el)
        except Exception as e:
            traceback.print_exc()
            print(
                f" >>>>>>>>>>>>>>>>>>>> Error in binding the answers: [{result}] <<<<<<<<<<<<<<<<<<"
            )

        result = {"head": {"vars": ["uri"]}, "results": {"bindings": bindings}}
        return True, result, False

    def get_names_and_uris(self, entity_query):
        root = ET.fromstring(self.evaluate_SPARQL_query(entity_query))
        uris_xml = root.findall(
            ".//{http://www.w3.org/2005/sparql-results#}results/{http://www.w3.org/2005/sparql-results#}result/{http://www.w3.org/2005/sparql-results#}binding/[@name='s']/{http://www.w3.org/2005/sparql-results#}uri"
        )
        names_xml = root.findall(
            ".//{http://www.w3.org/2005/sparql-results#}results/{http://www.w3.org/2005/sparql-results#}result/{http://www.w3.org/2005/sparql-results#}binding/[@name='o']/{http://www.w3.org/2005/sparql-results#}literal"
        )
        uris = [uri.text for uri in uris_xml]
        names = [name.text for name in names_xml]
        return uris, names

    def execute_sparql_query_and_get_uri_and_name_lists(self, q):
        cprint(f"== SPARQL Q Find E: {q}")
        root = ET.fromstring(self.evaluate_SPARQL_query(q))
        predicates_xml = root.findall(
            ".//{http://www.w3.org/2005/sparql-results#}results/{http://www.w3.org/2005/sparql-results#}result/{http://www.w3.org/2005/sparql-results#}binding/{http://www.w3.org/2005/sparql-results#}uri"
        )
        result = []
        for predicate in predicates_xml:
            result.append({"p": {"value": predicate.text}})
        return EndPoint.extract_predicate_names(self, result)


# TODO check if the answer type is compataible with what we are having (corresponds to check_if_answers_type_compatiable IN JSON endpoints)
# TODO extract the names of the resources
