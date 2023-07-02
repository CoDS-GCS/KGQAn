#!/bin/bash

# add required file's url to list
urls=(
    "http://206.12.94.177/CodsData/KGQAN/KGQAN_Models/seq2seq_model.zip"
    "http://206.12.94.177/CodsData/KGQAN/KGQAN_Models/wiki-news-300d-1M.txt.zip"
    # "https://storage.googleapis.com/allennlp-public-models/fine-grained-ner.2021-02-11.tar.gz"
    # "https://storage.googleapis.com/allennlp-public-models/ner-elmo.2021-02-12.tar.gz"
    # "https://storage.googleapis.com/allennlp-public-models/biaffine-dependency-parser-ptb-2020.04.06.tar.gz"
    # "https://storage.googleapis.com/allennlp-public-models/elmo-constituency-parser-2020.02.10.tar.gz"
)

# files will be stored in data directory
data_dir="./data"
mkdir -p "$data_dir"

for url in "${urls[@]}"
do
    file_name=$(basename "$url")
    extension="${file_name##*.}"
    
    # download the file using wget
    wget -v "$url" -P "$data_dir" -O "$data_dir/$file_name"
    
    # unzip it if its zip file
    if [ "$extension" = "zip" ]; then
        unzip "$data_dir/$file_name" -d "$data_dir"
        rm "$data_dir/$file_name" # remove the zip
    elif [ "$extension" = "tar" ] || [ "$extension" = "gz" ] || [ "$extension" = "bz2" ]; then
        tar -xf "$data_dir/$file_name" -C "$data_dir"
        rm "$data_dir/$file_name" # remove the tar
    fi
done
