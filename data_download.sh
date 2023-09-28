#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: ./data_download.sh [local|docker]"
    exit 1
fi

mode=$1


# add required file's url to list
urls=(
    "http://206.12.89.16/CodsData/KGQAN/KGQAN_Models/seq2seq_model.zip"
    "http://206.12.89.16/CodsData/KGQAN/KGQAN_Models/wiki-news-300d-1M.txt.zip"
)

# files will be stored in data directory
data_dir="./data"
mkdir -p "$data_dir"

wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1QbT5FDOJtdVd7AqZ-ekwUh2_pn6nNpb3' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1QbT5FDOJtdVd7AqZ-ekwUh2_pn6nNpb3" -O output_pred21_8_30.zip && rm -rf /tmp/cookies.txt
file_name="output_pred21_8_30.zip"
cp $file_name $data_dir/
unzip "$data_dir/$file_name" -d "$data_dir"
rm "$data_dir/$file_name" # remove the zip
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=149tB7x_dYLfmwoEdCfKfjBNeGdqFvqOP' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=149tB7x_dYLfmwoEdCfKfjBNeGdqFvqOP" -O wiki-news-300d-1M.zip && rm -rf /tmp/cookies.txt
file_name="wiki-news-300d-1M.zip"
cp $file_name $data_dir/
unzip "$data_dir/$file_name" -d "$data_dir"
rm "$data_dir/$file_name" # remove the zip

#for url in "${urls[@]}"
#do
#    file_name=$(basename "$url")
#    extension="${file_name##*.}"
#
#    # download the file using wget
#    wget -v "$url" -P "$data_dir" -O "$data_dir/$file_name"
#
#    # unzip it if its zip file
#    if [ "$extension" = "zip" ]; then
#        unzip "$data_dir/$file_name" -d "$data_dir"
#        rm "$data_dir/$file_name" # remove the zip
#    elif [ "$extension" = "tar" ] || [ "$extension" = "gz" ] || [ "$extension" = "bz2" ]; then
#        tar -xf "$data_dir/$file_name" -C "$data_dir"
#        rm "$data_dir/$file_name" # remove the tar
#    fi
#done

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

