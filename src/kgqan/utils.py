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

from itertools import chain, product, combinations


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

def get_combination_of_three_lists(list1, list2, list3, directed=False, with_reversed=False):
    lists = []
    # lists = [n1, p, n2]
    for node1 in list1:
        for node2 in list2:
            for predicate in list3:
                lists.append([node1, predicate, node2])
        return lists

def powerset(iterable, lower_bound=2, upper_bound=3):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    assert lower_bound < upper_bound
    upper_bound = upper_bound if (upper_bound <= len(s)) else len(s)+1
    lower_bound = lower_bound if (lower_bound >= 0) else 0
    return chain.from_iterable(combinations(s, r) for r in range(lower_bound, upper_bound))
