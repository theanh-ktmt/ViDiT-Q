# !/bin/bash
CKPT_PATH=$1
MODEL_NAME=$2

OPENSORA_CFG="t2v/configs/opensora/vbench/16x256x256.py"
CMD="python t2v/scripts/inference.py $OPENSORA_CFG"
OUTPUT="logs/eval/${MODEL_NAME}"
start=$(date +%s)

### Functions
# vbench has 950 samples
VBENCH_PROMPT_PATH="/home/tran/workspace/Open-Sora/assets/texts/VBench/all_dimension.txt"

function run_vbench() {
  eval $CMD \
    --ckpt_path $CKPT_PATH \
    --outdir $OUTPUT \
    --prompt_path $VBENCH_PROMPT_PATH
}

### Main
echo "Running vbench samples ..."
run_vbench


### End
end=$(date +%s)
runtime=$((end - start))
echo "Runtime: $runtime seconds"
