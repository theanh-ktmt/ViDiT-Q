import os

import torch
from mmengine.runner import set_random_seed
from opensora.datasets import save_sample
from opensora.registry import MODELS, SCHEDULERS, build_module
from opensora.utils.config_utils import parse_configs
from opensora.utils.misc import to_torch_dtype


### Helper functions ###
def load_prompts(prompt_path, start_idx=None, end_idx=None):
    with open(prompt_path, "r") as f:
        prompts = [line.strip() for line in f.readlines()]
    prompts = prompts[start_idx:end_idx]
    return prompts


def get_save_path_name(
    save_dir,
    sample_name=None,  # prefix
    sample_idx=None,  # sample index
    prompt=None,  # used prompt
    prompt_as_path=False,  # use prompt as path
    num_sample=1,  # number of samples to generate for one prompt
    k=None,  # kth sample
):
    if sample_name is None:
        sample_name = "" if prompt_as_path else "sample"
    sample_name_suffix = prompt if prompt_as_path else f"_{sample_idx:04d}"
    save_path = os.path.join(save_dir, f"{sample_name}{sample_name_suffix}")
    if num_sample != 1:
        save_path = f"{save_path}-{k}"
    return save_path


### MAIN ###
def main():
    # 1. cfg
    cfg = parse_configs(training=False)
    print(cfg)

    # 2. runtime variables
    torch.set_grad_enabled(False)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = to_torch_dtype(cfg.dtype)
    set_random_seed(seed=cfg.seed)

    start_idx = cfg.get("start_index", 0)
    end_idx = cfg.get("end_index", None)
    prompts = load_prompts(cfg.prompt_path, start_idx, end_idx)

    # 3. build model & load weights
    # 3.1. build scheduler
    scheduler = build_module(cfg.scheduler, SCHEDULERS)

    # 3.2. build model
    input_size = (cfg.num_frames, *cfg.image_size)
    vae = build_module(cfg.vae, MODELS)
    latent_size = vae.get_latent_size(input_size)
    model = build_module(
        cfg.model,
        MODELS,
        input_size=latent_size,
        in_channels=vae.out_channels,
        caption_channels=4096,  # DIRTY: for T5 only
        model_max_length=cfg.text_encoder.model_max_length,
        dtype=dtype,
    )
    if cfg.get("precompute_text_embeds", None) is not None:
        text_encoder = None
    else:  # normal loading of T5 from checkpoint
        text_encoder = build_module(
            cfg.text_encoder, MODELS, device=device
        )  # T5 must be fp32
        text_encoder.y_embedder = model.y_embedder  # hack for classifier-free guidance

    # 3.3. move to device & eval
    vae = vae.to(device, dtype).eval()
    model = model.to(device, dtype).eval()

    # 3.4. support for multi-resolution
    model_args = dict()
    if cfg.multi_resolution:
        image_size = cfg.image_size
        hw = torch.tensor([image_size], device=device, dtype=dtype).repeat(
            cfg.batch_size, 1
        )
        ar = torch.tensor(
            [[image_size[0] / image_size[1]]], device=device, dtype=dtype
        ).repeat(cfg.batch_size, 1)
        # Assume model_args is a dictionary that you might need to pass to the model
        model_args["data_info"] = dict(ar=ar, hw=hw)

    if cfg.get("precompute_text_embeds", None) is not None:
        model_args["precompute_text_embeds"] = torch.load(cfg.precompute_text_embeds)

    # TEMP: iter through timesteps
    # for ts in [10,15,20,25,30,40,50,75]:
    # cfg.scheduler.num_sampling_steps = ts
    # scheduler = build_module(cfg.scheduler, SCHEDULERS)

    # 4. inference
    model.timestep_wise_quant = False
    # sample_idx = 0
    save_dir = cfg.save_dir
    os.makedirs(save_dir, exist_ok=True)
    # assert len(prompts) % cfg.batch_size == 0, "no specified handling of drop_last, may cause errors"  # no handling of drop last
    for i in range(0, len(prompts), cfg.batch_size):
        print(
            "========== Prompt {}->{} / {} ==========".format(
                i, i + cfg.batch_size - 1, len(prompts)
            )
        )
        batch_prompts = prompts[i : i + cfg.batch_size]
        if (
            cfg.get("precompute_text_embeds", None) is not None
        ):  # also feed in the idxs for saved text_embeds
            model_args["batch_ids"] = torch.arange(i, i + cfg.batch_size)

        num_samples = cfg.get("num_samples", 1)
        for k in range(num_samples):
            print("> Processing sample {}th...".format(k + 1))
            save_paths = [
                get_save_path_name(
                    save_dir,
                    sample_name=None,
                    sample_idx=start_idx + idx,
                    prompt=batch_prompts[idx],
                    prompt_as_path=True,
                    num_sample=num_samples,
                    k=k,
                )
                for idx in range(len(batch_prompts))
            ]

            samples = scheduler.sample(
                model,
                text_encoder,
                sampler_type=cfg.sampler,
                z_size=(vae.out_channels, *latent_size),
                prompts=batch_prompts,
                device=device,
                additional_args=model_args,
            )
            samples = vae.decode(samples.to(dtype))

            for idx, sample in enumerate(samples):
                print(f"Prompt: {batch_prompts[idx]}")
                save_path = save_paths[idx]
                save_sample(sample, fps=cfg.fps, save_path=save_path)
                # sample_idx += 1


if __name__ == "__main__":
    main()
