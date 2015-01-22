#!/bin/sh

queries=$1

now=$(date +"%m_%d_%Y")
dirname=report_${now}
mkdir -p $dirname

echo 'Collecting ngrams'
python indexer.py tvindex.db /home/mkudinov/Data/Queries --drop-db

echo 'Getting PMI scores'
python main.py tvindex.db 2 
python main.py tvindex.db 3 2 
python main.py tvindex.db 4 3
python main.py tvindex.db 5 4
python main.py tvindex.db 6 5

echo 'Merging ngrams'
python ngram_prefix_tree.py tvindex.db > $dirname/cleaned1
python merge_postfix.py $dirname/cleaned1 > $dirname/cleaned
python sort_by_entropy.py $dirname/sort_by_entropy.py > $dirname/cleaned2

echo 'Cleaning and formatting'
python remove_by_stop_list.py feature_numerals feature_words $dirname/cleaned2> $dirname/result
echo 'Finished!'



