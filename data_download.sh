#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: ./data_download.sh [local|docker]"
    exit 1
fi

mode=$1


# add required file's url to list
urls=(
    "http://206.12.94.177/CodsData/KGQAN/KGQAN_Models/seq2seq_model.zip"
    "http://206.12.94.177/CodsData/KGQAN/KGQAN_Models/wiki-news-300d-1M.txt.zip"
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

if [ "$mode" = "local" ] | [ "$mode" = "docker" ]; then
    echo "Running Copy commands to run locally"
    # copy the file to the respective target path
    word_embedding_path="word_embedding/data"
    mkdir -p "$word_embedding_path"
    cp "./data/wiki-news-300d-1M.txt" "$word_embedding_path"

    kgqan_model_path="src/kgqan/model/"
    mkdir -p "$kgqan_model_path"
    cp -r ./data/output_pred21_8_30/* "$kgqan_model_path"
fi

