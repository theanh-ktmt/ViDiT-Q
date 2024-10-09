#!/bin/bash
GPU_ID=${1:-0}
CKPT_PATH="./logs/split_ckpt/OpenSora-v1-HQ-16x512x512-split.pth"
# MODEL_NAME="w8a8_ptqd"
MODEL_NAME="w6a6_naive_cb"

CUDA_VISIBLE_DEVICES=$GPU_ID \
bash t2v/shell_scripts/vbench/eval_quant.sh \
    $CKPT_PATH $MODEL_NAME