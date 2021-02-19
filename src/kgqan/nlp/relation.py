#!./venv python
# -*- coding: utf-8 -*-
"""
KGQAn: Natural Language Platform to Query Knowledge bases
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

# from transitions import Machine
from transitions.core import MachineError
from transitions.extensions import MachineFactory, GraphMachine as Machine
from transitions.extensions.states import add_state_features, Tags
from .models import WordNetLemmatizer
from .utils import nltk_POS_map

# cmd_folder = os.path.realpath(
#     os.path.dirname(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])))
#
# if cmd_folder not in sys.path:
#     sys.path.insert(0, cmd_folder)

lemmatizer = WordNetLemmatizer()


@add_state_features(Tags)
class CustomStateMachine(Machine):
    pass


class RelationLabeling(object):
    states = [{'name': 'unacceptable', 'tags': []},
              {'name': 'VB', 'tags': ['accepted']},
              {'name': 'VBD', 'tags': ['accepted']},
              {'name': 'VBD VBN', 'tags': ['accepted']},
              {'name': 'VBD NE', 'tags': []},
              {'name': 'VBN', 'tags': ['accepted']},
              {'name': 'VBP', 'tags': ['accepted']},
              {'name': 'VBZ', 'tags': ['accepted']},
              {'name': 'VBZ NE', 'tags': []},
              {'name': 'JJ', 'tags': []},
              {'name': 'NN', 'tags': ['accepted']},
              {'name': 'NNS', 'tags': ['accepted']},
              {'name': 'NE', 'tags': []},
              {'name': 'final', 'tags': ['accepted']}]

    def __init__(self):
        self.words = list()
        self.relation = list()
        self.relations = list()

        # Initialize the state machine
        # create a machine with mixins
        # Machine = MachineFactory.get_predefined(graph=True)
        # self.machine = Machine(model=self, states=RelationLabeling.states, initial='unacceptable')
        self.machine = CustomStateMachine(model=self, states=RelationLabeling.states, initial='unacceptable')

        self.machine.add_transition(trigger='VB', source='unacceptable', dest='VB', after='add_word')
        self.machine.add_transition(trigger='IN', source='VB', dest='final', after='add_word')
        self.machine.add_transition(trigger='NN', source='VB', dest='final', after='add_word')

        self.machine.add_transition(trigger='VBD', source='unacceptable', dest='VBD', after='add_word')
        self.machine.add_transition(trigger='IN', source='VBD', dest='final', after='add_word')
        self.machine.add_transition(trigger='VBN', source='VBD', dest='VBD VBN', after='add_word')
        self.machine.add_transition(trigger='IN', source='VBD VBN', dest='final', after='add_word')
        self.machine.add_transition(trigger='NE', source='VBD', dest='VBD NE')
        self.machine.add_transition(trigger='IN', source='VBD NE', dest='final', after='add_word')
        self.machine.add_transition(trigger='VBD', source='VBD NE', dest='final', after='add_word')

        self.machine.add_transition(trigger='VBN', source='unacceptable', dest='VBN', after='add_word')
        self.machine.add_transition(trigger='IN', source='VBN', dest='final', after='add_word')

        self.machine.add_transition(trigger='VBP', source='unacceptable', dest='VBP', after='add_word')
        self.machine.add_transition(trigger='IN', source='VBP', dest='final', after='add_word')

        self.machine.add_transition(trigger='VBZ', source='unacceptable', dest='VBZ', after='add_word')
        self.machine.add_transition(trigger='IN', source='VBZ', dest='final', after='add_word')
        self.machine.add_transition(trigger='NE', source='VBZ', dest='VBZ NE')
        self.machine.add_transition(trigger='VBN', source='VBZ NE', dest='final', after='add_word')

        self.machine.add_transition(trigger='VBG', source='unacceptable', dest='final', after='add_word')

        self.machine.add_transition(trigger='JJ', source='unacceptable', dest='JJ', after='add_word')
        self.machine.add_transition(trigger='NN', source='JJ', dest='final', after='add_word')
        self.machine.add_transition(trigger='IN', source='JJ', dest='final', after='add_word')

        self.machine.add_transition(trigger='NN', source='unacceptable', dest='NN', after='add_word') # 'NN', 'IN',
        self.machine.add_transition(trigger='NN', source='NN', dest='final', after='add_word')  ## Essam cases such as time zone
        self.machine.add_transition(trigger='NN', source='VBZ NE', dest='NN', after='add_word') ## birth name
        self.machine.add_transition(trigger='JJ', source='VBZ NE', dest='JJ', after='add_word') ## famous for
        self.machine.add_transition(trigger='IN', source='NN', dest='final', after='add_word')

        self.machine.add_transition(trigger='NE', source='unacceptable', dest='NE')
        self.machine.add_transition(trigger='RB', source='NE', dest='final', after='add_word')
        self.machine.add_transition(trigger='NN', source='NE', dest='final', after='add_word')

        self.machine.add_transition(trigger='VB', source=['VBZ NE', 'VBD NE', 'NE', 'NN', 'NNS'], dest='VB', before='clean_words', after='add_word')
        self.machine.add_transition(trigger='VBD', source=['VBD NE', 'NE', 'NN', 'NNS'], dest='VBD', before='clean_words', after='add_word')
        self.machine.add_transition(trigger='VBD', source=['VBD NE', 'NN', 'NN', 'NNS'], dest='VBD', before='clean_words', after='add_word')
        self.machine.add_transition(trigger='VBN', source=['VBD NE', 'NE', 'NN', 'NNS'], dest='VBN', before='clean_words', after='add_word')
        self.machine.add_transition(trigger='VBP', source=['VBD NE', 'NE', 'NN', 'NNS'], dest='VBP', before='clean_words', after='add_word')

        self.machine.add_transition(trigger='NNS', source='unacceptable', dest='NNS', after='add_word')  # 'NN', 'IN',
        self.machine.add_transition(trigger='IN', source='NNS', dest='final', after='add_word')

        self.machine.add_transition(trigger='NNS', source='JJ', dest='NNS', before='clean_words', after='add_word') # ID 24, 163 produced relations but questions not solved
        self.machine.add_transition(trigger='VBZ', source='NNS', dest='VBZ', before='clean_words', after='add_word') # ID 136, 111 error solved and nothing was affected
        self.machine.add_transition(trigger='VBP', source='VBZ NE', dest='VBP', before='clean_words', after='add_word') # ID 10 error solved and nothing was affected
        self.machine.add_transition(trigger='VBZ', source='JJ', dest='VBZ',  after='add_word') # ID 124 error solved and nothing was affected

    def add_word(self, word, pos):
        pos = nltk_POS_map.get(pos, pos)
        lemma = word
        if pos not in ['IN', 'RB']:
            lemma = lemmatizer.lemmatize(word, pos)
        self.words.append(lemma)
        if self.machine.get_state(self.state).is_accepted:
            self.relation.extend(self.words)
            self.words.clear()

    def clean_words(self, *args, **kwargs):
        self.flush_relation()
        self.words.clear()
        # self.words.append(word)

    def flush_relation(self):
        relation = ' '.join(self.relation)
        self.relations.append(relation)
        self.relation.clear()
        self.words.clear()
        self.to_unacceptable()


if __name__ == '__main__':
    kgqan_relation_extractor = RelationLabeling()
    pos = ['VB', 'IN']
    eval('kgqan_relation_extractor.VBG("starring")')
    # kgqan_relation_extractor.IN('for')
    try:
        kgqan_relation_extractor.VBDF('Mohamed')
    except AttributeError as ae:
        print(f'AttributeError: {ae}')
        print(kgqan_relation_extractor.accept_relation())
    except MachineError as me:
        print(f"MachineError: {me}")
        print(kgqan_relation_extractor.accept_relation())
    else:
        pass
    finally:
        print(kgqan_relation_extractor.state)
        kgqan_relation_extractor.get_graph().draw('my_state_diagram.png', prog='dot')
    # from graphviz import Digraph
    #
    # dot = Digraph(comment='The Round Table')
    # dot.node('A', 'King Arthur')
    # dot.node('B', 'Sir Bedevere the kgqan')
    # dot.node('L', 'Sir Lancelot the Brave')
    #
    # dot.edges(['AB', 'AL'])
    # dot.edge('B', 'L', constraint='false')
    # dot.render('test-output/round-table.gv', view=True)  # doctest: +SKIP




