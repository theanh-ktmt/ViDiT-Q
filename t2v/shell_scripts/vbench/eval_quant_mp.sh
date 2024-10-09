# !/bin/bash
CKPT_PATH=$1
MODEL_NAME=$2

OPENSORA_CFG="t2v/configs/opensora/vbench/16x256x256.py"
CMD="python t2v/scripts/quant_txt2video_mp.py $OPENSORA_CFG"
OUTPUT="logs/eval/${MODEL_NAME}"
MP_W_CONFIG="t2v/configs/quant/W4A8_Naive_Smooth/t20_weight_4_mp.yaml"  # the mixed precision config of weight
MP_A_CONFIG="t2v/configs/quant/W4A8_Naive_Smooth/t20_act_8_mp.yaml" # the mixed precision config of act
start=$(date +%s)

### Functions
# vbench has 950 samples
VBENCH_PROMPT_PATH="/home/tran/workspace/Open-Sora/assets/texts/VBench/all_dimension.txt"

function run_vbench() {
  eval $CMD \
    --ckpt_path $CKPT_PATH \
    --outdir $OUTPUT \
    --prompt_path $VBENCH_PROMPT_PATH \
    --part_fp --dataset_type opensora \
    --timestep_wise_mp \
	--time_mp_config_weight $MP_W_CONFIG \
	--time_mp_config_act $MP_A_CONFIG
}

### Main
echo "Running vbench samples ..."
run_vbench

### End
end=$(date +%s)
runtime=$((end - start))
echo "Runtime: $runtime seconds"
