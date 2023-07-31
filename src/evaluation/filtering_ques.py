import sys

import os
import json
import traceback
from itertools import count
from termcolor import colored, cprint

from kgqan.kgqan import KGQAn


max_Vs = 1
max_Es = 40
max_answers = 40
limit_VQuery = 400
limit_EQuery = 300

file_dir = os.path.dirname(os.path.abspath(__file__))
file_name = os.path.join(file_dir, "lcquad1/lcquad-qaldformat-test2.json")
indices_file_test = os.path.join(file_dir, "lcquad1/TestingIDs_LCQuAD1.txt")

def extracting_e(text_sparql):
    entity_list = list()
    dot_split = text_sparql.split(" . ")

    for i in range(len(dot_split)):
        if 'OPTIONAL' in dot_split[i]:
            text_sparql.replace(dot_split[i], "")
        else:
            space_split = dot_split[i].split(" ")
            for j in range(len(space_split)):
                if 'WHERE' in space_split:
                    if "?" not in space_split[-1]:
                        if space_split[-1] not in entity_list:
                            entity_list.append(space_split[-1].replace('<', "").replace('>', ""))
                    if "?" not in space_split[-3]:
                        if space_split[-3] not in entity_list:
                            entity_list.append(space_split[-3].replace('<', "").replace('>', ""))
                else:
                    if "?" not in space_split[-3] and "" not in space_split[-3] and "}" not in space_split[-3]:
                        entity_list.append(space_split[-3].replace('<', "").replace('>', ""))
                    if "?" not in space_split[-1] and "" not in space_split[-1] and "}" not in space_split[-1]:
                        entity_list.append(space_split[-1].replace('<', "").replace('>', ""))
    return entity_list

def extract_boolean(sparql):
    # print("SPARQL is")
    # print(sparql)
    entity_list = list()
    open_braces = sparql.index('{')
    close_braces = sparql.index('}')
    triples = sparql[open_braces + 1: close_braces].strip()
    triples_list = triples.split(' . ')
    for triple in triples_list:
        triple = triple.strip()
        if 'OPTIONAL' in triple:
            continue
        components = triple.split(' ')
        for i, component in enumerate(components):
            if i == 1 or component.strip().startswith('?'):
                continue
            component = component[1:-1].strip()
            entity_list.append(component)
    #print(entity_list)
    return entity_list

def extract_boolean_predicate(sparql):
    #print('In Function')
    predicate_list = list()
    open_braces = sparql.index('{')
    close_braces = sparql.index('}')
    triples = sparql[open_braces + 1: close_braces].strip()
    triples_list = triples.split(' . ')
    for triple in triples_list:
        triple = triple.strip()
        if 'OPTIONAL' in triple:
            continue
        components = triple.split(' ')
        for i, component in enumerate(components):
            if i == 0 or i == 2 or component.strip().startswith('?'):
                continue
            component = component[1:-1].strip()
            #print(component)
            predicate_list.append(component)
    #print('Predicate List')
    #print(predicate_list)
    return predicate_list


def extracting_v(text_sparql):
    predicate_list = list()
    dot_split = text_sparql.split(" . ")
    for s in range(len(dot_split)):
        if 'OPTIONAL' in dot_split[s]:
            text_sparql.replace(dot_split[s], "")
        else:
            space_split = dot_split[s].split(" ")
            for j in range(len(space_split)):
                if 'WHERE' in space_split:
                    if space_split[-2] not in predicate_list:
                        predicate_list.append(space_split[-2].replace('<', "").replace('>', ""))
                    else:
                        if "?" not in space_split[1] and "" not in space_split[1] and "}" not in space_split[1]:
                            predicate_list.append(space_split[1].replace('<', "").replace('>', ""))
    return predicate_list


def keeping(ans):
    if 'boolean' in ans:
        return True  # Stays
    if ans['results'] and len(ans['results']) > 0:
        return True  # Stays
    else:
        return False  # Bye bye


if __name__ == '__main__':
    entity_mapping = list()
    predicate_mapping = list()

    keep_list = list()
    remove_list = list()

    ans_predicate = list()
    
    filtered_predicate = list()
    unfiltered_predicate = list()

    indices = []
    with open(indices_file_test) as(f):
        for line in f:
            indices.append(int(line))

    with open(file_name) as f:
        qald9_test = json.load(f)
    dataset_id = qald9_test['dataset']['id']

    MyKGQAn = KGQAn(n_max_answers=max_answers, n_max_Vs=max_Vs, n_max_Es=max_Es,
                    n_limit_VQuery=limit_VQuery, n_limit_EQuery=limit_EQuery)

    qCount = count(1)
    res = []
    counter = 0
    for i, question in enumerate(qald9_test['questions']):
        counter += 1

        if int(question['id']) not in indices:
            continue

        # if int(question['id']) not in [3, 4, 5, 9, 16, 62]:
        #     continue

        entity_mapping = set()
        predicate_mapping = set()
        
        #counter += 1
        qc = next(qCount)
        for language_variant_question in question['question']:
            if language_variant_question['language'] == 'en':
                question_text = language_variant_question['string'].strip()
                break
        text = colored(f"[PROCESSING: ] Question count: {qc}, ID {question['id']}  >>> {question_text}", 'blue',
                       attrs=['reverse', 'blink'])
        cprint(f"== {text}  ")
        try:
            #answers, vertices, predicates, graph = MyKGQAn.ask(question_text=question_text,
                                                              # answer_type=question['answertype'], question_id=question['id'], knowledge_graph='dbpedia')
            answers, vertices, predicates, _, _, _ = MyKGQAn.ask(question_text=question_text,
                                                                                question_id=question['id'], knowledge_graph='lc_quad')
        except Exception as e:
            traceback.print_exc()
            continue

        for answer in answers:
            sparql = answer['sparql']
            uri = ["uri"]
            if 'boolean' in answer:
               extracted_e = extract_boolean(sparql)
               extracted_v = extract_boolean_predicate(sparql)
            else:
                extracted_e =extract_boolean(sparql)
                extracted_v =extract_boolean_predicate(sparql)

            # if extracted_e not in entity_mapping:
            #     entity_mapping.append(extracted_e)
            #
            # if extracted_v not in predicate_mapping:
            #     predicate_mapping.append(extracted_v)
            for e in extracted_e:
                entity_mapping.add(e)
            for e in extracted_v:
                predicate_mapping.add(e)

            #if keeping(answer):
            #    keep_list.append(predicate_mapping)
            #else:
            #    remove_list.append(predicate_mapping)
            
        #if predicate_mapping in remove_list and predicate_mapping not in keep_list:
        #    filtered_predicate.append(predicate_mapping)
        #else:
        #    unfiltered_predicates = predicate_mapping

        ent_dict_list = list()
        for e in entity_mapping:
            ent_dict_list.append({'uri': e})

        pred_dict_list = list()
        for p in predicate_mapping:
            pred_dict_list.append({'uri': p})

        #filtered_dict_pred = list()
        #for p in unfiltered_predicates:
        #    filtered_dict_pred.append(({'uri': p}))

        linking_filter = {"question": question_text, "SerialNumber": question['id'],
                              "sparql_query": question['query']['sparql'],
                              "entity mapping": ent_dict_list, "predicate mapping": pred_dict_list}

        # linking_filter = {"question": question_text, "SerialNumber": question['id'],
        #                           "sparql_query": question['query']['sparql'],
        #                           "entity mapping": entity_mapping, "predicate mapping": unfiltered_predicates}
        res.append(linking_filter)
        #if counter == 10:
            #print("LF =", linking_filter)
         #   break
    json_object = json.dumps(res, indent=4, ensure_ascii=False)

    with open(os.path.join(file_dir, f'output/FilteringLinkingquesBoolean.json'), "w", encoding='utf-8') as outfile:
        outfile.write(json_object)

# "SELECT ?uri WHERE { ?uri <http://dbpedia.org/ontology/country> <http://dbpedia.org/resource/United_States> .
# ?uri <http://dbpedia.org/ontology/capital> ?capital .
# ?uri <http://dbpedia.org/property/densityrank> ?density .
# OPTIONAL {?uri <http://www.w3.org/2000/01/rdf-schema#label> ?string.
