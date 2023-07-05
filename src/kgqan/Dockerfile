FROM python:3.7

ADD requirements.txt ./app/requirements.txt
RUN pip3 install --upgrade pip 
RUN pip3 install --debug -r /app/requirements.txt
RUN python -m spacy download en_core_web_sm

ADD . ./app
WORKDIR app

RUN useradd appuser && chown -R appuser /app
USER appuser
ENV ALLENNLP_CACHE_ROOT="."

RUN python nltk_setup.py
CMD ["python", "server.py"]
