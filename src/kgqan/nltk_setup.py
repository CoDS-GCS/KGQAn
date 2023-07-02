import nltk
import os

cache_dir = "nltk_cache"
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir, exist_ok=True)

nltk.data.path.append(cache_dir)
nltk.download('wordnet', download_dir=cache_dir)
nltk.download('punkt', download_dir=cache_dir)

nltk.corpus.wordnet.ensure_loaded()
