#!/bin/bash
GPU_ID=${1:-0}
CKPT_PATH="./logs/split_ckpt/OpenSora-v1-HQ-16x512x512-split.pth"
MODEL_NAME="full_fp16"

CUDA_VISIBLE_DEVICES=GPU_ID \
bash t2v/shell_scripts/vbench/eval_fp16.sh \
    $CKPT_PATH $MODEL_NAME
