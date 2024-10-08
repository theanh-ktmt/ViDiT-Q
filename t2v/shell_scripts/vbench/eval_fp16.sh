# !/bin/bash
CKPT=$1
MODEL_NAME=$2

CMD="python t2v/scripts/inference.py t2v/configs/opensora/vbench/16x512x512.py"
OUTPUT="logs/eval/${MODEL_NAME}/generated_videos"
start=$(date +%s)
DEFAULT_BS=1
DEFAULT_SAMPLING_STEPS=30

### Functions
# vbench has 950 samples
VBENCH_BS=1 # 80GB
VBENCH_PROMPT_PATH="/home/tran/workspace/Open-Sora/assets/texts/VBench/all_dimension.txt"

function run_vbench() {
  eval $CMD --ckpt_path $CKPT --save_dir ${OUTPUT}_vbench \
    --prompt_path $VBENCH_PROMPT_PATH \
    --batch_size $VBENCH_BS
}

### Main
echo "Running vbench samples ..."
run_vbench


### End
end=$(date +%s)
runtime=$((end - start))
echo "Runtime: $runtime seconds"
