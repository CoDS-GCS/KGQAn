#!./venv python
# -*- coding: utf-8 -*-
"""
KGQAn: Natural Language Platform to Query Knowledge bases
"""
__lab__ = "CoDS Lab"
__copyright__ = "Copyright 2020-29, GINA CODY SCHOOL OF ENGINEERING AND COMPUTER SCIENCE, CONCORDIA UNIVERSITY"
__credits__ = ["CoDS Lab"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "CODS Lab"
__email__ = "essam.mansour@concordia.ca"
__status__ = "debug"
__created__ = "2020-02-07"
from allennlp.predictors.predictor import Predictor
from nltk.stem import WordNetLemmatizer
import nltk


# oie = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/openie-model.2018-08-20.tar.gz")
# ner = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/ner-model-2018.12.18.tar.gz")
ner = Predictor.from_path(
    "https://storage.googleapis.com/allennlp-public-models/fine-grained-ner.2021-02-11.tar.gz")

elmo_ner = Predictor.from_path(
    "https://storage.googleapis.com/allennlp-public-models/ner-elmo.2021-02-12.tar.gz")

parser = Predictor.from_path(
    "https://storage.googleapis.com/allennlp-public-models/biaffine-dependency-parser-ptb-2020.04.06.tar.gz")
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()
