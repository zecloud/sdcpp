import json
import os
#from time import sleep
import random
from io import BytesIO
from cachetools import cached,LRUCache
from stable_diffusion_cpp import StableDiffusion
from dapr.clients import DaprClient
from dapr.ext.grpc import App, BindingRequest
from huggingface_hub import snapshot_download,hf_hub_download
import logging
#from cloudevents.sdk.event import v1
#from dapr.clients.grpc._response import TopicEventResponse
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import threading

logging.basicConfig(level = logging.INFO)
app = App()
#should_retry = True  
#DAPR_INPUT_STORE_NAME="hotshotoutput"
#DAPR_STORE_NAME=os.getenv("DAPR_STORE_NAME", "statestore")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME", "fluxstorageaca")
account_url="https://"+ACCOUNT_NAME+".blob.core.windows.net"
CONTAINER_NAME = os.getenv("CONTAINER_NAME","fluxjob")
#tmpdir="/home/outputs/tmp/"
MAX = 64 * 1024 * 1024 # 64MB
SUPERMAX = 512 * 1024 * 1024 # 512MB

def dlmodels():
    #modelpath=hf_hub_download(repo_id="leejet/FLUX.1-schnell-gguf", filename="flux1-schnell-q2_k.gguf",local_dir="pretrained_models")
    #modelpath=hf_hub_download(repo_id="leejet/FLUX.1-schnell-gguf", filename="flux1-schnell-q8_0.gguf",local_dir="pretrained_models")
    #modelpath=hf_hub_download(repo_id="leejet/FLUX.1-dev-gguf", filename="flux1-dev-q3_k.gguf",local_dir="pretrained_models")
    modelpath=hf_hub_download(repo_id="leejet/FLUX.1-dev-gguf", filename="flux1-dev-q8_0.gguf",local_dir="pretrained_models")
    
    
    #vaepath=hf_hub_download(repo_id="black-forest-labs/FLUX.1-dev", filename="ae.safetensors",local_dir="pretrained_models")
    vaepath=hf_hub_download(repo_id="Green-Sky/flux.1-schnell-GGUF", filename="ae-f16.gguf",local_dir="pretrained_models")
    
    #clippath=hf_hub_download(repo_id="comfyanonymous/flux_text_encoders", filename="clip_l.safetensors",local_dir="pretrained_models")
    #t5path=hf_hub_download(repo_id="comfyanonymous/flux_text_encoders", filename="t5xxl_fp16.safetensors",local_dir="pretrained_models")
    clippath=hf_hub_download(repo_id="Green-Sky/flux.1-schnell-GGUF", filename="clip_l-q8_0.gguf",local_dir="pretrained_models")
    #clippath=hf_hub_download(repo_id="zer0int/CLIP-GmP-ViT-L-14", filename="ViT-L-14-TEXT-detail-improved-hiT-GmP-TE-only-HF.safetensors",local_dir="pretrained_models")

   
    t5path=hf_hub_download(repo_id="Green-Sky/flux.1-schnell-GGUF", filename="t5xxl_q8_0.gguf",local_dir="pretrained_models")
    return modelpath,vaepath,clippath,t5path

lock = threading.RLock()
cache = LRUCache(maxsize=1)
@cached(cache=cache,lock=lock)
def initstabledif():    
    modelpath,vaepath,clippath,t5path=dlmodels()
    stable_diffusion = StableDiffusion(
        diffusion_model_path=modelpath, # In place of model_path
        clip_l_path= clippath,
        t5xxl_path=t5path,
        vae_path=vaepath,
        vae_decode_only=True, # Can be True if we dont use img_to_img
        diffusion_flash_attn=True,
        lora_model_dir="./pretrained_models/lora/",
        verbose = True
    )
    return stable_diffusion

# def message_handler(message_content):
#     """
#     Fonction personnalisée pour gérer les messages.
    
#     :param message_content: Contenu du message provenant de la file d'attente.
#     """
#     imgrequested=json.loads(message_content)
#     genimg(imgrequested)

def runstabledif(stable_diffusion,prompt,width,height):
    seed = random.randint(0, 2 ** 32 - 1)
    output = stable_diffusion.txt_to_img(
        prompt=prompt,
        sample_steps=25,
        cfg_scale=1.0, # a cfg_scale of 1 is recommended for FLUX
        sample_method="euler", # euler is recommended for FLUX
        seed=seed,
        width=width,
        height=height,
    )
    bIO = BytesIO()
    output[0].save(bIO, format="PNG")
    data_bytes=bIO.getvalue()
    return data_bytes

def genimg(params):
    stable_diffusion=initstabledif()
    prompt=params["prompt"]
    folder=params["folder"]
    idsave=params["idsave"]
    width=params.get("width",512)
    height=params.get("height",512)
    data_bytes=runstabledif(stable_diffusion,prompt,width,height)
    publish_and_save(data_bytes,folder,idsave)

def azureupload(pathfile,data):
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=pathfile)
    blob_client.upload_blob(data)

def publish_and_save(img,folder,idsave):
  #stringimg = base64.b64encode(image).decode('utf-8')
  with DaprClient(max_grpc_message_length=MAX) as client:
        #Using Dapr SDK to save and get state
        outputfile=folder+"/"+idsave+".png"
        azureupload(outputfile,img)
        #client.save_state(DAPR_STORE_NAME, outputfile, img) 
        req_data = {'message':  outputfile} 
        # Create a typed message with content type and body
        resp = client.publish_event(
            pubsub_name='pubsubcomponent',
            topic_name=f'finishedfluxjob',#/{idsave}
            data=json.dumps(req_data),
            data_content_type='application/json',
            publish_metadata={'rawPayload': 'true'},
        )
        logging.info('Published data: message sent')
        print('sent message and saved')

#@app.subscribe(pubsub_name='pubsubcomponent', topic='fluxjob')
#def mytopic(event: v1.Event) -> TopicEventResponse:
@app.binding('fluxjobbinding')
def mytopic(request: BindingRequest):
    #global should_retry
    #data = json.loads(event.Data())
    data = json.loads(request.text())
    print(f'Received: idsave={data["idsave"]}, prompt="{data["prompt"]}"' 
          ' content_type="{event.content_type}"',flush=True)
    try:
        genimg(data)
    except Exception as e:
        print(f"Error processing message: {e}")
        #return TopicEventResponse('drop')
    # if should_retry:
    #     should_retry = False  # we only retry once in this example
    #     sleep(0.5)  # add some delay to help with ordering of expected logs
    #     return TopicEventResponse('retry')
    #return TopicEventResponse('success')

# @app.binding('holavatarsinput')
# def incoming(request: BindingRequest):
#     incomingtext = request.text()
#     print(">>>>>>>Message Received: "+ incomingtext,flush=True)

if __name__ == '__main__':
    app.register_health_check(lambda: print('Healthy'))
    app.run(50051)