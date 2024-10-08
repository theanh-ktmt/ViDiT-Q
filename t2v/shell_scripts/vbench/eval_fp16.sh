# !/bin/bash
CKPT=$1
MODEL_NAME=$2

CMD="python t2v/scripts/inference.py t2v/configs/opensora/vbench/16x256x256.py"
OUTPUT="logs/eval/${MODEL_NAME}"
start=$(date +%s)
DEFAULT_BS=1
DEFAULT_SAMPLING_STEPS=30

### Functions
# vbench has 950 samples
VBENCH_PROMPT_PATH="/home/tran/workspace/Open-Sora/assets/texts/VBench/all_dimension.txt"

function run_vbench() {
  eval $CMD --ckpt_path $CKPT --outdir $OUTPUT \
    --prompt_path $VBENCH_PROMPT_PATH
}

### Main
echo "Running vbench samples ..."
run_vbench


### End
end=$(date +%s)
runtime=$((end - start))
echo "Runtime: $runtime seconds"
