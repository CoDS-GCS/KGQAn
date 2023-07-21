# Run KGQAn in Dockerized environment

## Prerequisites
- Docker: Ensure that you have Docker installed on your machine. If not, follow the installation instructions specific to your operating system:
  - [Install Docker for Windows](https://docs.docker.com/desktop/windows/install/)
  - [Install Docker for Linux](https://docs.docker.com/engine/install/)
  - [Install Docker for macOS](https://docs.docker.com/desktop/mac/install/)

- Docker Compose: Verify that you have Docker Compose installed by running the following command:

```shell
docker-compose version
```
- If Docker Compose is not installed, you can follow the instructions to install it:
 - [Install Docker Compose](https://docs.docker.com/compose/install/)


## Setup Instructions
1. Clone the repository:
```shell
git clone https://github.com/CoDS-GCS/KGQAn.git
cd KGQAn
```

## Download the required data/models:
- Run the following command to execute the data download script:
- This script will download the trained models and any necessary data for the services.
```shell
# run in docker environment
./data_download.sh docker
```

## *Note* : KGQAn server depends on Word Embedding Server, Word Embedding server takes arround ~3.5 minute time to load w2v file. So there is 300 seconds delay in docker run.

## Build and run the services using Docker Compose:
- Make sure you are in the root directory of the project.
- To start KGQAn in server mode use docker-compose-server.yml
```shell
docker-compose -f docker-compose-server.yml up --build
```

- To start KGQAn in evaluation mode use docker-compose-evaluation.yml
```shell
docker-compose -f docker-compose-evaluation.yml up --build
```
- The evaluation results for benchmarks [QALD, DBLP, LCQUAD, YAGO, MAG] will be stored in src/evaluation/output/evaluation_results.csv
- It will be in below format
```csv
Benchmark Name
P, R, F1
xx, xx, xx
```

## Access the services (Start in server mode):
- Once the Docker containers are up and running, you can access the services using the specified URLs or ports.
```shell
curl -X POST -H "Content-Type: application/json" -d '{"question": "Who founded Intel?", "knowledge_graph":"dbpedia", "max_answers": 3}' localhost:8899
```

## Clean up:
- To stop and remove the running Docker containers, use the following command:
```shell
docker-compose down
```
