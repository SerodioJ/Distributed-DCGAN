#!/bin/bash

samples=3;
results_path="results"
nproc=4
batch_size=32

trap "exit" INT
while getopts s:r:p:b: flag
do
    case "${flag}" in
        s) samples=$OPTARG;;
        r) results_path=$OPTARG;;
        p) nproc=$OPTARG;;
        b) batch_size=$OPTARG;;
    esac
done

[ -e $results_path/proc-${nproc}_batch-${batch_size}.csv ] && rm $results_path/proc-${nproc}_batch-${batch_size}.csv
for counter in $(seq 1 $samples); do
    echo Starting nproc_per_node=$nproc batch_size=$batch_size $counter of $samples
    start=$(date +%s%3N)
    docker run --env OMP_NUM_THREADS=1 --rm --network=host -v=$(pwd):/root \
        dist_dcgan:latest python -m torch.distributed.launch --nproc_per_node=$nproc --master_addr="172.17.0.1" --master_port=1234 \
        dist_dcgan.py --dataset cifar10 --dataroot ./cifar10 --batch_size $batch_size --num_epochs 1 | grep "Epoch 0 took" | cut -d " " -f 6 | tr '\n' ',' >> $results_path/proc-${nproc}_batch-${batch_size}.csv
    printf "\n" >> $results_path/proc-${nproc}_batch-${batch_size}.csv
    end=$(date +%s%3N)
    echo nproc_per_node=$nproc batch_size=$batch_size Runs: $counter/$samples.
    echo took $((end-start)) milliseconds.
    
done
