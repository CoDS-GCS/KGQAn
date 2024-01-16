Reproducing Results in Paper
-----
To reproduce the results in the paper, you need to follow the process explained here from the root directory of the proect
The following process needs to be followed from the `KGQAn` directory

1._**Source Code and Benchmarks**_

- The code is available at the following GitHub Repository: https://github.com/CoDS-GCS/KGQAn.git 
- It can be downloaded using the following command: git clone https://github.com/CoDS-GCS/KGQAn.git
- Benchmarks can be found in the following directory src/evaluation/data/ 
  1. **QALD-9**: qald-9-test-multilingual.json
  2. **LCQuAD-1.0**: lcquad-qaldformat-test2.json 
  3. **YAGO**: qald9_yago100.json
  4. **DBLP**: qald9_dblp100.json
  5. **MAG**: qald9_ms100.json

2. _**Description of software/library dependencies**_
    - KGQAn can run in two settings local mode and docker mode, for ease of reproducing the results we will follow the docker set up mode
    - docker setup steps: https://github.com/CoDS-GCS/KGQAn/blob/docker-setup/docker_run.md 
    - If you want to run in the local mode: you can follow the steps specified here: https://github.com/CoDS-GCS/KGQAn#running-kgqan
    - The system was mainly tested using the ubuntu OS

3. _**Description of hardware needed**_
    - For KGQAn to run, we will need around 32GB of RAM to start the server at the begining, after the start up no special hardware is needed
4. _**Detailed fully automated scripts**_
      Choose between steps 1&2, step 1 runs in the docker mode, step 2 runs in the local mode. step3 produce the figures using the output values
      1.  To get the results in docker mode: **docker_run.sh**:
         - The docker script for creating the container and running the evaluation scripts of the five benchmarks and producing their results
         ```shell
         ./docker_run.sh
         ```
         - It consists of the following steps:
           1. Navigating to the KGQAn directory
           2. Downloading the required files
           3. Calling `docker compose` to run the evaluation and return all results in `output` directory
           4. The output opip install traitletsf this script are: `evaluation_results.csv` and `evaluation_response_time.csv`
           5. `evaluation_result.csv` contain the results of the following the five benchmarks besides the results for the filtration and linking experiment, in the following order:
              - QALD
              - LCQUAD-1.0
              - YAGO
              - DBLP
              - MAG
              - QALD with filtration disabled
              - LCQUAD with filtration disabled
              - Entity Linking
              - Relation Linking
         - If you encountered an error while running this script due to the `docker compose` command, you can install it from [here](https://docs.docker.com/compose/install/) 
         - If you have a problem running the docker compose line because of permission errors, you can follow the solution from [here][https://docs.docker.com/engine/install/linux-postinstall/] 
         - If you have a problem running the script because of `Version in "./docker-compose-evaluation.yml"` Error, you can replace the 'version' parameter in `docker-compose-server.yml` and `docker-compose-evaluation.yml`
         
           **If you do not want to run in a docker mode then you can run in local mode using the following steps:**
            - To get the results in local mode **local_run.sh**:
            - A prerequisite to running in this mode is to run the semantic affinity server using this commands: 
               ```
               conda activate kgqan
               python word_embedding/server.py 127.0.0.1 9600
              ```
              ```shell
                 ./local_run.sh
              ```
            - It runs each of the benchmarks evaluation python script to produce the Json output
            - It evaluates the produced Json against the ground truth values

      2. **figures_generation.sh**:
               - First create a virtual environment and install the required dependencies 
               ```shell
               conda create --name figures python==3.7
               conda activate figures
               pip install matplotlib pandas traitlets
               ./figures_generation.sh
               ```
               - The generation script is responsible for generating the four figures as pdf file in this directory, The generated figures are:
                 1. **question understanding quality**: The values here were obtained manually by checking the logs for KGQAn and existing systems
                 2. **Linking quality**: To produce the figure, the scores of the entity linking and relation linking are obtained from `evaluation_result.csv`. The values are organized in the following order [Entity Precision, Entity Recall, Entity F1, Relation Precision, Relation Recall, Relation F1]
                 3. **Filtering quality**: To produce the figure, the scores of QALD-no-filtration, LCQAUD-no-filtration, QALD and LCQAUD  are obtained from `evaluation_result.csv`. The values are organized in the following order [QALD Precision, QALD Recall, QALD F1, LCQuAD Precision, LCQUAD Recall, LCQUAD F1]
                 4. **Response time per benchmark**: To produce the figure, the response times are obtained from `evaluation_response_time.csv`. The values are organized in the following orders [QALD, LCQuAD, YAGO, DBLP, MAG].
5. _**Documentation**_
   - Each script contains its documentaion for all steps performed
6. _**A single master script**_:
   - We divided our operation into two scripts as the results of the first is needed to get the figures from the second script 
   - The Question understanding failure values were obtained by manually checking the logs of KGQAn and exisiting systems for the question understanding step 
   - The linking values were obtained by extracting the outputs of the linking from the final SPARQL queries of all systems
   - The response time values in the output file `evaluation_response_time.csv` are used in `Figures/response_time.py`
   - The F1 score values in the output file `evaluation_results.csv` are used in `Figures/filtering.py`
7. _**An estimation of the deployment time and effort**_
   1. These estimates are obtained by running on a machine of 180 GB of RAM and 16 cores 
   2. Downloading the required files + creating the docker image + enabling the servers ~30 minutes (depends on the internet connection speed)
   2. Running the five benchmarks and evaluating their results + Filtering and Linking experiments ~ 8 hours
   3. Producing the Figures ~5 minutes

### Mapping Between Experiments and Paper Results
The final outputs produced after all experiments finish running are saved in two main files:
1. `src/evaluation/output/evaluation_results.csv`: This file contains the results of 9 Experiments:  1) QALD, 2) LCQuAD, 3)YAGO, 4) DBLP, 5)MAG, 6)QALD with filtration disabled, 7)LCQUAD with filtration disabled, 8)Entity Linking, 9)Relation Linking
2. `src/evaluation/output/evaluation_response_time.csv`: Response time for running the main experiment 

Here is the mapping between the Experiments and the Tables and Figures of the Paper

| Table / Figure | Experiment                                 |
|----------------|--------------------------------------------|
| Table 3        | `evaluation_results.csv`: Experiments 1-5  |
| Figure 7       | `evaluation_response_time.csv`             |
 | Figure 9       | `evaluation_results.csv`: Experiments 8, 9 | 
| Figure 10 | `evaluation_results.csv`: Experiments 1,2, 6, 7|



