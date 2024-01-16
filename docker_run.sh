#!/bin/bash
# Move to the KGQAn directory
cd KGQAn
# Download the required model and files
./data_download.sh docker
# Create the docker container and run the five benchmakrs
docker compose -f docker-compose-evaluation.yml up --build