import os
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

class Seq2SeqModel:
    """
    Singleton
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,model_path):
        self.model = None
        self.tokenizer = None
        if os.path.exists(model_path):
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            print("Seq2Seq model loaded...")
        else:
            print("Invalid Seq2Seq model path")

file_dir = os.path.dirname(os.path.abspath(__file__))
seq2seq_model_path = os.path.join(file_dir, "model")
print(seq2seq_model_path)
seq2seq_model = Seq2SeqModel(seq2seq_model_path)
