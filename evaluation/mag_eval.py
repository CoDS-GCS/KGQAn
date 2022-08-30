#!./venv python
# -*- coding: utf-8 -*-
"""
evaluation.py: evaluating KGQAn online service against QALD-3 benchmark
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

import sys

sys.path.append('../src/')

import json
import time
import traceback

from kgqan import KGQAn
from termcolor import colored, cprint
from itertools import count
import xml.etree.ElementTree as Et

file_name = r"mag/qald9_ms100.json"

if __name__ == '__main__':
    root_element = Et.Element('dataset')
    root_element.set('id', 'dbpedia-test')
    author_comment = Et.Comment(f'created by CoDS Lab')
    root_element.append(author_comment)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    total_time = 0
    total_understanding_time = 0
    total_linking_time = 0
    total_execution_time = 0

    # The main param:
    # max no of vertices and edges to annotate the PGP
    # max no of SPARQL queries to be generated from PGP
    max_Vs = 1
    max_Es = 21
    max_answers = 41
    limit_VQuery = 600
    limit_EQuery = 300

    with open(file_name) as f:
        qald9_testset = json.load(f)
    dataset_id = qald9_testset['dataset']['id']
    MyKGQAn = KGQAn(n_max_answers=max_answers, n_max_Vs=max_Vs, n_max_Es=max_Es,
                    n_limit_VQuery=limit_VQuery, n_limit_EQuery=limit_EQuery)
    qCount = count(1)

    kgqan_qald9 = {"dataset": {"id": "qald9_ms100"}, "questions": []}
    for i, question in enumerate(qald9_testset['questions']):
        qc = next(qCount)
        for language_variant_question in question['question']:
            if language_variant_question['language'] == 'en':
                question_text = language_variant_question['string'].strip()
                break

        text = colored(f"[PROCESSING: ] Question count: {qc}, ID {question['id']}  >>> {question_text}", 'blue',
                       attrs=['reverse', 'blink'])
        cprint(f"== {text}  ")

        st = time.time()
        # question_text = 'Which movies starring Brad Pitt were directed by Guy Ritchie?'
        # question_text = 'When did the Boston Tea Party take place and led by whom?'
        try:
            answers, _, _, understanding_time, linking_time, execution_time\
                = MyKGQAn.ask(question_text=question_text,
                              question_id=question['id'], knowledge_graph='microsoft_academic')
        except Exception as e:
            traceback.print_exc()
            continue

        all_bindings = list()
        for answer in answers:
            if answer['results'] and answer['results']['bindings']:
                all_bindings.extend(answer['results']['bindings'])

        try:
            if 'results' in question['answers'][0]:
                question['answers'][0]['results']['bindings'] = all_bindings.copy()
                all_bindings.clear()
        except:
            question['answers'] = []

        kgqan_qald9['questions'].append(question)

        et = time.time()
        total_time = total_time + (et - st)
        total_understanding_time = total_understanding_time + understanding_time
        total_linking_time = total_linking_time + linking_time
        total_execution_time = total_execution_time + execution_time
        text = colored(f'[DONE!! in {et - st:.2f} SECs]', 'green', attrs=['bold', 'reverse', 'blink', 'dark'])
        cprint(f"== {text} ==")

        # break
    text1 = colored(f'total_time = [{total_time:.2f} sec]', 'yellow', attrs=['reverse', 'blink'])
    text2 = colored(f'avg time = [{total_time / qc:.2f} sec]', 'yellow', attrs=['reverse', 'blink'])
    cprint(f"== QALD 9 Statistics : {qc} questions, Total Time == {text1}, Average Time == {text2} ")
    cprint(f"== Understanding : {qc} questions, Total Time == {total_understanding_time}, Average Time == {total_understanding_time / qc} ")
    cprint(f"== Linking : {qc} questions, Total Time == {total_linking_time}, Average Time == {total_linking_time / qc} ")
    cprint(f"== Execution : {qc} questions, Total Time == {total_execution_time}, Average Time == {total_execution_time / qc}")

    with open(f'output/MyKGQAn_result_{timestr}_MaxAns{max_answers}_MaxVs{max_Vs}_MaxEs{max_Es}'
              f'_limit_VQuery{limit_VQuery}_limit_VQuery{limit_EQuery}_TTime{total_time:.2f}Sec_Avgtime{total_time / qc:.2f}Sec.json',
              encoding='utf-8', mode='w') as rfobj:
        json.dump(kgqan_qald9, rfobj)
        rfobj.write('\n')
