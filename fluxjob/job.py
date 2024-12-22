import logging
import json
import os
from huggingface_hub import snapshot_download,hf_hub_download
from io import BytesIO
import traceback
from stable_diffusion_cpp import StableDiffusion
from msgprocessor import MessageVisibilityManager
from blockprocessor import BlobManager
from queueprocessor import QueueManager


connection_string = os.environ.get("azstorageconnstring")
blob_container_name =os.environ.get("BLOBCONTAINERNAME")
input_queue_name =os.environ.get("INPUTQUEUENAME") 
finished_queue_name =os.environ.get("FINISHEDQUEUENAME")


def message_handler(message_content):
    """
    Fonction personnalisée pour gérer les messages.
    
    :param message_content: Contenu du message provenant de la file d'attente.
    """
    imgrequested=json.loads(message_content)
    genimage(imgrequested)

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
     #
    #hallo_dir = snapshot_download(repo_id="leejet/FLUX.1-schnell-gguf", local_dir="pretrained_models")

def callback(step: int, steps: int, time: float):
    print("Completed step: {} of {}".format(step, steps))


def genimage(params):
    modelpath,vaepath,clippath,t5path=dlmodels()
    prompt=params["prompt"]
    folder=params["folder"]
    idsave=params["idsave"]
    stable_diffusion = StableDiffusion(
        diffusion_model_path=modelpath, # In place of model_path
        clip_l_path= clippath,
        t5xxl_path=t5path,
        vae_path=vaepath,
        vae_decode_only=True, # Can be True if we dont use img_to_img
        verbose = True
    )

    #with tempfile.TemporaryDirectory() as tmpdirname:
    #    with tempfile.NamedTemporaryFile(dir=tmpdirname,suffix=".png", delete=True) as imgfile:
    try:
        output = stable_diffusion.txt_to_img(
            prompt=prompt,
            sample_steps=4,
            cfg_scale=1.0, # a cfg_scale of 1 is recommended for FLUX
            sample_method="euler", # euler is recommended for FLUX
            progress_callback=callback,
        )   
    except Exception as e:
        traceback.print_exc()
        print("Test - flux failed: ", e)
        return
    bIO = BytesIO()
    output[0].save(bIO, format="PNG")
    data_bytes=bIO.getvalue()
    publish_and_save(data_bytes,folder,idsave)

def publish_and_save(video,folder,idsave):
  #stringimg = base64.b64encode(image).decode('utf-8')
    client=BlobManager(connection_string, blob_container_name) 
    #Using Dapr SDK to save and get state
    outputfile=folder+"/"+idsave+".png"
    client.upload_blob(outputfile, video) 
    req_data = {'message':  outputfile} 

    queue_client:QueueManager = QueueManager(connection_string,finished_queue_name)
    queue_client.send_message( json.dumps(req_data))

    logging.info('Published data: message sent')
    print('sent message and saved')


def main():
    queue_client:QueueManager = QueueManager(connection_string,input_queue_name)
    try:
        incomingtext,msg_id, msg_popreceipt,msg_dequeueCount=queue_client.receive_message()
    except TypeError as te:
        print("No message found in the queue")
        return
    except Exception as e:
        print(f"Error receiving message: {e}")
        raise e
    print(">>>>>>>Message Received: "+ incomingtext,flush=True)

    if(msg_dequeueCount<6):
        visibility_manager = MessageVisibilityManager(
            connectionstring=connection_string,
            message_id=msg_id,
            pop_receipt=msg_popreceipt,
            queuename=input_queue_name,
            visibility_timeout=100
        )
      # Démarrer le processus de mise à jour de la visibilité
        visibility_manager.start()
        try:
            message_handler(incomingtext)
        except Exception as e:
            print(f"Error processing message: {e}")
            visibility_manager.stop()
            raise e
        # Arrêter la mise à jour de la visibilité
        visibility_manager.stop()

        # Supprimer le message après traitement
        visibility_manager.delete_message()

if __name__ == '__main__':
    main()