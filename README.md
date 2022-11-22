 KGQAn - A Universal Question-Answering Platform for Knowledge Graphs 
 ---
 - - - - -
![GitHub Logo](logo/architecture.png)

KGQAn is a universal question answering Platform to answer questions on Knowledge graphs. It can deal with different
knowledge graphs without the need to pre-process on each graph. KGQAn runs in three phases: 1) Question understanding phase
that construct triple patterns from the question using a Sequence to Sequence model then converts the triple patterns to 
a phrase graph pattern (PGP). 2) JIT linking phase to link the nodes and edges of the PGP to vertices and predicates from
the KG without using any pre-created index. 3) Execution and post-filtering phase to create the SPARQL query from the linked
PGP, execute it and filters the list of answers returned then the answers are sent to the user.


Installation
-----------
- - - - 
* Clone the repo
* Create `kgqan` Conda environment (Python 3.7) and install pip requirements.
```
conda create --name kgqan python=3.7
pip install -r requirements.txt
```
* Download the word embeddings file: `wiki-news-300d-1M.txt.zip`:  
https://drive.google.com/file/d/1UTPGv8QUgqSVQ2JeX9QVW0YhbGRxONLL/view?usp=sharing
* Unzip the downloaded file and put it under `word_embedding` directory
* Download the trained question understanding model: https://drive.google.com/file/d/1QbT5FDOJtdVd7AqZ-ekwUh2_pn6nNpb3/view?usp=sharing
* Unzip the downloaded directory and put it under `models` directory

Running KGQAn
------------
- - - - 

KGQAn uses a semantic similarity model in two of its phases, a pre-requisite step is to run the server of the
word-embedding based similarity service using the following command
 ```
 conda activate kgqan
 python word_embedding/server.py 127.0.0.1 9600
 ```
You can run KGQAn in two modes:
1. Batch processing: This is used to run benchmarks or pre-defined set of questions
2. Server mode: This is used to answer individual questions

### Batch processing ###
KGQAn takes as an input a JSON file containing all questions in the following format:
```
{
    "question": 
    [
        {
            "string": question text
            "language": "en"
        }
   ],
   "id": question id,
   "answers": []
}
```
* To run KGQAn in this mode, you need a script that opens the questions' file then calls KGQAn module to answer the questions.
* To call the KGQAn module you should use the following code:
```python
from kgqan import KGQAn
my_kgqan = KGQAn()
answers = my_kgqan.ask(question_text=question_text, question_id=question['id'], knowledge_graph=knowledge_graph)
```
* check `evaluation/qald9eval.py` as an example.
### Server ###
KGQAn takes as an input: the question, the knowledge graph and the maximum number of answers the user wants to be returned

To run KGQAn in this mode:
1. Open the KGQAn server by running the following command from the `src` directory
```
conda activate kgqan
python -m kgqan.kgqan_server.server
```
2. Wait until the following message shows to be sure the server is running successfully
```
Server started http://0.0.0.0:8899
```
3. Send a POST request to the server with the question, the knowledge graph to query and the maximum number of answers required using
   * Postman
   * CURL
   ```
        curl -X POST -H "Content-Type: application/json" \
        -d '{"question": "Who founded Intel?", "knowledge_graph": "dbpedia", "max_answers": 3}' \
        http://0.0.0.0:8899
   ```

Benchmarks:
-
- - - -
1. QALD-9:
   1. https://github.com/ag-sc/QALD/blob/master/9/data/qald-9-test-multilingual.json
   2. Put the downloaded benchmark under `qald` directory
2. LCQUAD:
   1. https://figshare.com/articles/dataset/LC-QuAD_QALDformat/5818452
   2. Put the downloaded benchmark under `lcquad` directory
3. YAGO: Will be released soon
4. DBLP: Will be released soon
5. MAG: Will be released soon
