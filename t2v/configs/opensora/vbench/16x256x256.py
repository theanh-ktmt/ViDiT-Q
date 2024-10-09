num_frames = 16
fps = 24 // 3
image_size = (256, 256)

# Define model
model = dict(
    type="STDiT-XL/2",
    space_scale=0.5,
    time_scale=1.0,
    enable_flashattn=True,
    enable_layernorm_kernel=False,
    from_pretrained="PRETRAINED_MODEL",
)
vae = dict(
    type="VideoAutoencoderKL",
    from_pretrained="stabilityai/sd-vae-ft-ema",
    # micro_batch_size=2,
)
text_encoder = dict(
    type="t5",
    from_pretrained="DeepFloyd/t5-v1_1-xxl",
    model_max_length=120,
)
scheduler = dict(
    type="iddpm",
    num_sampling_steps=30,
    cfg_scale=7.0,
)
dtype = "fp16"
# Others
batch_size = 4
seed = 42
prompt_path = "t2v/assets/texts/t2v_samples.txt"
# save_dir = "./generated_videos/fp16"

# Vbench
num_samples = 5
start_index = 0
end_index = 2000
