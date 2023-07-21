#!/bin/bash

# Set the PATH to include the Ruby binary
export PATH="/root/.rbenv/shims:$PATH"

# check if an argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 [server|evaluation]"
    exit 1
fi


case "$1" in
    server)
        echo "Waiting for word_embedding_server to load model"
        waittime=300
        sleep $waittime && echo "waited for 300 sec, till word_embd_server loaded model"
        python -m kgqan.server
        ;;
    evaluation)
        echo "Waiting for word_embedding_server to load model"
        waittime=300
        sleep $waittime && echo "waited for 300 sec, till word_embd_server loaded model"
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

        echo "Evaluation Completed!, results can be found at src/evaluation/output/evaluation_results.csv"
        python -m kgqan.server
        ;;
    *)
        echo "Invalid argument. Usage: $0 [server|evaluation]"
        exit 1
        ;;
esac
