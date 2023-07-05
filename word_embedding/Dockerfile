FROM python:3.7

ADD requirements.txt ./app/requirements.txt
RUN pip3 install --upgrade pip 
RUN pip3 install --debug -r /app/requirements.txt

ADD . ./app
WORKDIR app

RUN useradd appuser && chown -R appuser /app
USER appuser

CMD ["python", "server.py"]
