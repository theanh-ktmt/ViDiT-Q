#!/bin/bash
CKPT_PATH="./logs/split_ckpt/OpenSora-v1-HQ-16x512x512-split.pth"
MODEL_NAME="full_fp16"

CUDA_VISIBLE_DEVICES=2 \
bash t2v/shell_scripts/eval/eval_fp16.sh \
    $CKPT_PATH $MODEL_NAME
