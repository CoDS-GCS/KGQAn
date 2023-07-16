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

import json
import os
import time
from termcolor import colored, cprint
from itertools import count
import xml.etree.ElementTree as Et
from kgqan.kgqan import KGQAn

file_dir = os.path.dirname(os.path.abspath(__file__))

the_39_question_ids = (1, 3, 8, 9, 11, 13, 14, 15, 16, 17, 21, 23, 24, 26, 27, 28, 30, 31, 33, 35, 37, 39, 40, 41, 43,
                       47, 54, 56, 61, 62, 64, 68, 75, 83, 85, 92, 93, 96, 99)
file_name = os.path.join(file_dir, "qald6/qald-6-test-multilingual.json")


if __name__ == '__main__':
    root_element = Et.Element('dataset')
    root_element.set('id', 'dbpedia-test')
    author_comment = Et.Comment(f'created by CoDS Lab')
    root_element.append(author_comment)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    the_39_questions = list()
    total_time = 0

    max_Vs = 1
    max_Es = 21
    max_answers = 41

    with open(file_name) as f:
        qald6_testset = json.load(f)
    dataset_id = qald6_testset['dataset']['id']
    MyKGQAn = KGQAn(n_max_answers=max_answers, n_max_Vs=max_Vs, n_max_Es=max_Es)
    count39 = count(1)
    kgqan_qald6 = {"dataset": {"id": "qald-6-test-multilingual"}, "questions": []}
    for i, question in enumerate(qald6_testset['questions']):
        # if question['id'] not in the_39_question_ids:
        #     continue
        qc = next(count39)


        # question_text = ''
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
        answers = MyKGQAn.ask(question_text=question_text, answer_type=question['answertype'])

        all_bindings = list()
        for answer in answers:
            if answer['results'] and answer['results']['bindings']:
                all_bindings.extend(answer['results']['bindings'])

        try:
            if 'results' in question['answers'][0]:
                question['answers'][0]['results']['bindings'] = all_bindings.copy()
                kgqan_qald6['questions'].append(question)
                all_bindings.clear()
        except:
            question['answers'] = []

        et = time.time()
        total_time = total_time + (et - st)
        text = colored(f'[DONE!! in {et-st:.2f} SECs]', 'green', attrs=['bold', 'reverse', 'blink', 'dark'])
        cprint(f"== {text} ==")

        # break
    text1 = colored(f'total_time = [{total_time:.2f} sec]', 'yellow', attrs=['reverse', 'blink'])
    text2 = colored(f'avg time = [{total_time / qc:.2f} sec]', 'yellow', attrs=['reverse', 'blink'])
    cprint(f"== QALD 9 Statistics : {qc} questions, Total Time == {text1}, Average Time == {text2} ")

    with open(f'output/MyKGQAn_result_{timestr}_MaxAns{max_answers}_MaxVs{max_Vs}_MaxEs{max_Es}'
              f'_TTime{total_time:.2f}Sec_Avgtime{total_time / qc:.2f}Sec.json',
              encoding='utf-8', mode='w') as rfobj:
        json.dump(kgqan_qald6, rfobj)
        rfobj.write('\n')

