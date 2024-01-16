#!/bin/bash
# Move to the KGQAn directory
cd KGQAn
# Download the required model and files
#./data_download.sh local
# Run the five benchmarks
output_path="evaluation/output1"
mkdir -p "$output_path"

python -m evaluation.qald9_eval
ruby evaluation/evaluation.rb evaluation/output/qald.json QALD

python -m evaluation.lcquad_eval
ruby evaluation/evaluation.rb evaluation/output/lcquad.json LCQUAD

python -m evaluation.yago_eval
ruby evaluation/evaluation.rb evaluation/output/yago.json YAGO

python -m evaluation.dblp_eval
ruby evaluation/evaluation.rb evaluation/output/dblp.json DBLP

python -m evaluation.mag_eval
ruby evaluation/evaluation.rb evaluation/output/mag.json MAG

python evaluation/merge_files.py

python -m evaluation.qald9_eval --filter False
ruby evaluation/evaluation.rb evaluation/output/qald.json QALD-NO-Filtration

python -m evaluation.lcquad_eval --filter False
ruby evaluation/evaluation.rb evaluation/output/lcquad.json LCQUAD-NO-Filtration

python -m evaluation.filtering_ques
python evaluation/calculate_score_linking.py
