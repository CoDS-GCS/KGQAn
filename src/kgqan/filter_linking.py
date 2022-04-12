import json
import traceback
from itertools import count

from kgqan import KGQAn
from kgqan.kgqan_server.server import max_answers, max_Vs, limit_EQuery, max_Es, limit_VQuery

file_name = r"qald9/qald-9-test-multilingual.json"


def extracting_e(text_sparql):
    entity_list = list()
    sparql_split = text_sparql.split(".")

    for i in range(len(sparql_split)):
        if 'OPTIONAL' in sparql_split[i]:
            text_sparql.replace(sparql_split[i], "")
        else:
            space_split = sparql_split[i].split(" ")
            for j in range(len(space_split)):
                if 'WHERE' in space_split:
                    w_index = space_split.index('{')
                    if "?" not in space_split[w_index + 1]:
                        entity_list.append(space_split[w_index + 1])
                    if "?" not in space_split[w_index + 3]:
                        entity_list.append(space_split[w_index + 3])
                else:
                    if "?" not in space_split[0]:
                        entity_list.append(space_split[0])
                    if "?" not in space_split[2]:
                        entity_list.append(space_split[2])
    return entity_list


def extracting_v(text_sparql):
    predicate_list = list()
    dot_split = text_sparql.split(".")

    for s in range(len(dot_split)):
        if 'OPTIONAL' in dot_split[s]:
            text_sparql.replace(dot_split[s], "")
        else:
            space_split = dot_split[i].split(" ")
            for j in range(len(space_split)):
                if 'WHERE' in space_split:
                    w_index = space_split.index('{')
                    predicate_list.append(space_split[w_index + 2])
                else:
                    predicate_list.append(space_split[1])
    return predicate_list


if __name__ == '__main__':
    entities = list()
    predicates = list()

    with open(file_name) as f:
        qald9_test = json.load(f)
    dataset_id = qald9_test['dataset']['id']

    MyKGQAn = KGQAn(n_max_answers=max_answers, n_max_Vs=max_Vs, n_max_Es=max_Es,
                    n_limit_VQuery=limit_VQuery, n_limit_EQuery=limit_EQuery)

    qCount = count(1)
    res = []
    for i, question in enumerate(qald9_test['questions']):
        qc = next(qCount)
        for language_variant_question in question['question']:
            if language_variant_question['language'] == 'en':
                question_text = language_variant_question['string'].strip()
                break

        try:
            answers, vertices, predicates, graph = MyKGQAn.ask(question_text=question_text,
                                                               answer_type=question['answertype'],
                                                               question_id=question['id'], knowledge_graph='dbpedia')
        except Exception as e:
            traceback.print_exc()
            continue

        for answer in answers:
            if answer['results'] and len(answer['results']) > 0:
                sparql = answer['sparql']
                entities.append(extracting_e(sparql))
                predicates.append(extracting_v(sparql))
                linking_filter = {"question": question_text, "SerialNumber": question['id'], "sparql_query": sparql,
                                  "entity mapping": entities, "predicate mapping": predicates}
                res.append(linking_filter)

    json_object = json.dumps(res, indent = 4, ensure_ascii=False)

    with open("FiteringLinking.json", "w", encoding='utf-8') as outfile:
        outfile.write(json_object)

# "SELECT ?uri WHERE { ?uri <http://dbpedia.org/ontology/country> <http://dbpedia.org/resource/United_States> .
# ?uri <http://dbpedia.org/ontology/capital> ?capital .
# ?uri <http://dbpedia.org/property/densityrank> ?density .
# OPTIONAL {?uri <http://www.w3.org/2000/01/rdf-schema#label> ?string.
