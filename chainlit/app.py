import chainlit as cl
from stable_diffusion_cpp import StableDiffusion
import random
from chainlit import make_async
from io import BytesIO
from huggingface_hub import snapshot_download,hf_hub_download

def dlmodels():
    modelpath=hf_hub_download(repo_id="leejet/FLUX.1-schnell-gguf", filename="flux1-schnell-q2_k.gguf",local_dir="pretrained_models")
    #modelpath=hf_hub_download(repo_id="leejet/FLUX.1-schnell-gguf", filename="flux1-schnell-q8_0.gguf",local_dir="pretrained_models")
    #modelpath=hf_hub_download(repo_id="leejet/FLUX.1-dev-gguf", filename="flux1-dev-q3_k.gguf",local_dir="pretrained_models")
    
    
    #vaepath=hf_hub_download(repo_id="black-forest-labs/FLUX.1-dev", filename="ae.safetensors",local_dir="pretrained_models")
    vaepath=hf_hub_download(repo_id="Green-Sky/flux.1-schnell-GGUF", filename="ae-f16.gguf",local_dir="pretrained_models")
    
    #clippath=hf_hub_download(repo_id="comfyanonymous/flux_text_encoders", filename="clip_l.safetensors",local_dir="pretrained_models")
    #t5path=hf_hub_download(repo_id="comfyanonymous/flux_text_encoders", filename="t5xxl_fp16.safetensors",local_dir="pretrained_models")
    clippath=hf_hub_download(repo_id="Green-Sky/flux.1-schnell-GGUF", filename="clip_l-q8_0.gguf",local_dir="pretrained_models")
    #clippath=hf_hub_download(repo_id="zer0int/CLIP-GmP-ViT-L-14", filename="ViT-L-14-TEXT-detail-improved-hiT-GmP-TE-only-HF.safetensors",local_dir="pretrained_models")

   
    t5path=hf_hub_download(repo_id="Green-Sky/flux.1-schnell-GGUF", filename="t5xxl_q8_0.gguf",local_dir="pretrained_models")
    return modelpath,vaepath,clippath,t5path


#asyncdlmodels =make_async(dlmodels)
@cl.cache
def initstabledif():    
    modelpath,vaepath,clippath,t5path=dlmodels()
    stable_diffusion = StableDiffusion(
        diffusion_model_path=modelpath, # In place of model_path
        clip_l_path= clippath,
        t5xxl_path=t5path,
        vae_path=vaepath,
        vae_decode_only=True, # Can be True if we dont use img_to_img
        verbose = True
    )
    return stable_diffusion

sdcache=initstabledif()
asyncinitstabledif =make_async(initstabledif)

def runstabledif(stable_diffusion,prompt):
    seed = random.randint(0, 2 ** 32 - 1)
    output = stable_diffusion.txt_to_img(
        prompt=prompt,
        sample_steps=4,
        cfg_scale=1.0, # a cfg_scale of 1 is recommended for FLUX
        sample_method="euler", # euler is recommended for FLUX
        seed=seed,
    )
    bIO = BytesIO()
    output[0].save(bIO, format="PNG")
    data_bytes=bIO.getvalue()
    return data_bytes

asyncrunstabledif =make_async(runstabledif)

@cl.on_chat_start
async def on_chat_start():
    #stable_diffusion=sdcache#await asyncinitstabledif()
    print("A new chat session has started!")
    #cl.user_session.set("stablediffusion", stable_diffusion)

@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...
    stable_diffusion = sdcache#cl.user_session.get("stablediffusion")
    output = await asyncrunstabledif(stable_diffusion, message.content)
    # Send a response back to the user
    image = cl.Image(content=output, name="image1", display="inline"),
    await cl.Message(
        content=f"prompt: {message.content}",
        elements=image,
    ).send()
