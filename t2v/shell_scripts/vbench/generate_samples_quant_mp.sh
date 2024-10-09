#!/bin/bash
GPU_ID=${1:-0}
CKPT_PATH="./logs/split_ckpt/OpenSora-v1-HQ-16x512x512-split.pth"
MODEL_NAME="w4a8_timestep_aware_cb"

CUDA_VISIBLE_DEVICES=$GPU_ID \
bash t2v/shell_scripts/vbench/eval_quant_mp.sh \
    $CKPT_PATH $MODEL_NAME