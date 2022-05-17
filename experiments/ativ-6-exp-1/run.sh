#!/bin/bash

python -m torch.distributed.launch --nproc_per_node=$1 --nnodes=$2 --node_rank=$NODE_RANK --master_addr=$3 --master_port=1234 \
    dist_dcgan.py --dataset cifar10 --dataroot ./cifar10 --batch_size $4 --num_epochs 1 | grep "Epoch 0 took" | cut -d " " -f 6 | tr '\n' ','