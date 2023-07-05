import string
import os
import sys
import numpy as np
import statistics
import chars2vec



class WordEmbeddings:
    def __init__(self, model_path):
        self.model_path = model_path
        self.w = None
        self.vocab = None
        self.ivocab = None
        self.vector_feature_size = 0
        self.char2vec = chars2vec.load_model("eng_300")

    def load_model(self):
        self.w, self.vocab, self.ivocab = self.load_vocab()

    def load_vocab(self):
        with open(self.model_path, "r") as f:
            words = [x.rstrip().split(" ")[0] for x in f.readlines()]
        with open(self.model_path, "r") as f:
            vectors = {}
            for line in f:
                vals = line.rstrip().split(" ")
                vectors[vals[0]] = [float(x) for x in vals[1:]]

        vocab_size = len(words)
        vocab = {w: idx for idx, w in enumerate(words)}
        ivocab = {idx: w for idx, w in enumerate(words)}

        vector_dim = len(vectors[ivocab[0]])
        global vector_feature_size
        vector_feature_size = vector_dim
        W = np.zeros((vocab_size, vector_dim))
        for word, v in vectors.items():
            if word == "<unk>":
                continue
            W[vocab[word], :] = v

        # normalize each word vector to unit variance
        W_norm = np.zeros(W.shape)
        d = np.sum(W**2, 1) ** (0.5)
        W_norm = (W.T / d).T
        return (W_norm, vocab, ivocab)

    def semantic_distance(self, v1, v2):
        if v1 is None or v2 is None:
            print("unknowns")
            return -99
        else:
            sim = np.dot(v1, v2.T)
        return sim

    def get_embedding_for_word(self, word):
        # print("vocab", )
        # print(len(vocab))
        if word in self.vocab:
            return self.w[self.vocab[word], :]
        else:
            return None

    def mwe_semantic_distance(self, vs1, vs2):
        cmp_count = 0
        sims = list()
        for v1 in vs1:
            for v2 in vs2:
                cmp_count += 1
                if v1 is None:
                    # TODO: use minimum edit distance
                    sims.append(0.0)
                    continue
                if v2 is None:
                    sims.append(0.0)
                    continue
                sim = np.dot(v1, v2.T) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                sims.append(sim)
        else:
            return statistics.mean(sims)

    def get_embedding_for_mwe(self, mwe):
        mwe = mwe.translate(str.maketrans("", "", string.punctuation))
        words = mwe.strip().split()
        mwe_vecs = list()

        for w in words:
            if w in self.vocab:
                mwe_vecs.append(self.w[self.vocab[w], :])
            else:
                vec = self.char2vec.vectorize_words([w])
                vec = vec.astype(float)
                mwe_vecs.append(vec[0])
        else:
            return mwe_vecs




if __name__ == "__main__":
    wiki_model = WordEmbeddings(
        r"/home/disooqi/projects/wise/word_embedding/wiki-news-300d-1M.txt"
    )
    wiki_model.load_model()
    print("Done loading")
    print(
        "ss: "
        + str(
            wiki_model.semantic_distance(
                wiki_model.get_embedding_for_word("wife"),
                wiki_model.get_embedding_for_word("spouse"),
            )
        )
    )
