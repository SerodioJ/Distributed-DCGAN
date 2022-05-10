#!/bin/bash

samples=3;
results_path="results"

trap "exit" INT
while getopts s:r: flag
do
    case "${flag}" in
        s) samples=$OPTARG;;
        r) results_path=$OPTARG;;
    esac
done

# Batch 32
./experiment_base.sh -s $samples -r $results_path -p 1 -b 32

./experiment_base.sh -s $samples -r $results_path -p 2 -b 32

./experiment_base.sh -s $samples -r $results_path -p 4 -b 32

# ./experiment_base.sh -s $samples -r $results_path -p 8 -b 32 # Uncomment this if machine has enough memory

# Batch 16
./experiment_base.sh -s $samples -r $results_path -p 1 -b 16

./experiment_base.sh -s $samples -r $results_path -p 2 -b 16

./experiment_base.sh -s $samples -r $results_path -p 4 -b 16

./experiment_base.sh -s $samples -r $results_path -p 8 -b 16

