import os
from typing import List
from utils import encode_video_to_base64
import torch
from diffusers import CogVideoXPipeline
from diffusers.utils import export_to_video

from diffusers import AutoencoderKLCogVideoX, CogVideoXImageToVideoPipeline, CogVideoXTransformer3DModel
from diffusers.utils import export_to_video, load_image
from transformers import T5EncoderModel, T5Tokenizer
import torch
model_path = 'model_cache'   # The local directory to save downloaded checkpoint

model_id=model_path

# from diffusers.pipelines.stable_diffusion.safety_checker import (
#     StableDiffusionSafetyChecker,
# )


MODEL_ID = "THUDM/CogVideoX-5b"
MODEL_CACHE = "diffusers-cache"
# SAFETY_MODEL_ID = "CompVis/stable-diffusion-safety-checker"


class Predictor:
    def setup(self):
        """Load the model into memory to make running multiple predictions efficient"""
        print("Loading pipeline...")
        # safety_checker = StableDiffusionSafetyChecker.from_pretrained(
        #     SAFETY_MODEL_ID,
        #     cache_dir=MODEL_CACHE,
        #     local_files_only=True,
        # )
        transformer = CogVideoXTransformer3DModel.from_pretrained(model_id, subfolder="transformer",
                                                                  torch_dtype=torch.float16)
        text_encoder = T5EncoderModel.from_pretrained(model_id, subfolder="text_encoder", torch_dtype=torch.float16)
        vae = AutoencoderKLCogVideoX.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float16)
        tokenizer = T5Tokenizer.from_pretrained(model_id, subfolder="tokenizer")
        self.pipe = CogVideoXPipeline.from_pretrained(model_id, tokenizer=tokenizer, text_encoder=text_encoder,
                                                 transformer=transformer, vae=vae, torch_dtype=torch.float16).to("cuda")


        # self.pipe.enable_xformers_memory_efficient_attention()

    @torch.inference_mode()
    def predict(self, prompt, number_of_frames,num_inference_steps, guidance_scale,fps):
        if torch.cuda.is_available():
            print('=============cuda available==================')
            generator = torch.Generator('cuda').manual_seed(42)
        else:
            print('=============cuda not available==============')
            generator = torch.Generator().manual_seed(42)
        print('inference')
        video = self.pipe(
            prompt=prompt,
            num_videos_per_prompt=1,
            num_inference_steps=num_inference_steps,
            num_frames=number_of_frames,
            guidance_scale=guidance_scale,
            generator=generator,
        ).frames[0]

        file_name = "new_out.mp4"
        export_to_video(video, file_name, fps=fps)

        encoded_frames = encode_video_to_base64(file_name)
        return encoded_frames


