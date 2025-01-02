import chainlit as cl
import json
import time
import os
import asyncio
from dapr.aio.clients import DaprClient
from cloudevents.sdk.event import v1
#from dapr.ext.grpc import App
#from dapr.clients.grpc._response import TopicEventResponse
import uuid
import re 
from azure.servicebus.aio import ServiceBusClient
from azure.identity.aio import DefaultAzureCredential


FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
QUEUE_NAME = os.environ.get("SERVICEBUS_QUEUE_NAME", "finishedfluxjob")
DAPR_STORE_NAME=os.getenv("DAPR_STORE_NAME", "fluxstatestore")
MAX = 64 * 1024 * 1024 # 64MB

@cl.on_chat_start
async def on_chat_start():
    
    print("A new chat session has started!")

    
@cl.on_message
async def main(message: cl.Message):
     
   
    # Your custom logic goes here...
    await cl.Message(
        content=f"prompt: {message.content}",
        #elements=image,
    ).send()
    stabledif = await diststabledif(message.content)
    pathimage=json.loads(stabledif)
    
    async with DaprClient(max_grpc_message_length=MAX) as client:
        #Using Dapr SDK to save and get state
        outputfile=pathimage["message"]
        resp =await client.get_state(DAPR_STORE_NAME, outputfile)
        image=resp.data
        
    await cl.Message(
        content=f"{outputfile}",
        elements=image,
    ).send()

# async def process_message(message) -> TopicEventResponse:
#     """
#     Asynchronously processes the message and returns a TopicEventResponse.
#     """

#     print(f'Processing message: {message.data()} from {message.topic()}...', flush=True)
#     global in_progress
#     in_progress = False
#     return TopicEventResponse('success')

@cl.step(name="image generator...")
async def diststabledif(prompt:str):
    async with DaprClient() as d:
        #idsave=string_to_filename(prompt)
        idsave = str(uuid.uuid4())
        req_data = {"prompt":prompt,"folder":"chainlit","idsave":idsave }
#{'id': id, 'message': 'hello world'}

        # Create a typed message with content type and body
        await d.publish_event(
            pubsub_name='pubsubcomponent',
            topic_name='fluxjob',
            data=json.dumps(req_data),
            data_content_type='application/json',
            publish_metadata={ 'rawPayload': 'true'},
        )
        
        #global in_progress
        #in_progress = True
        credential = DefaultAzureCredential()
        servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential)

        async with servicebus_client:
            receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
            async with receiver:
                received_msgs = await receiver.receive_messages(max_message_count=1, max_wait_time=600)
                msg = received_msgs[0]  
                #for msg in received_msgs:
                print(str(msg))
                # await cl.Message(
                #         content=f"{msg}",
                #         #elements=image,
                #     ).send()
                await receiver.complete_message(msg)
                return str(msg)
        # close_fn = await d.subscribe_with_handler(
        #     pubsub_name='pubsubcomponent', topic='finishedfluxjob/{idsave}', handler_fn=process_message,
        #     dead_letter_topic='finishedfluxjob/{idsave}_DEAD'
        # )
        
        #while in_progress:
        #     await asyncio.sleep(1)
        #global img
        

        # print("Closing subscription...")
        # await close_fn()

    #return "message envoyé"

def string_to_filename(input_string):
    # Remplacer les caractères non valides par des underscores
    filename = re.sub(r'[^\w\-_\. ]', '_', input_string)
    # Optionnel: Tronquer le nom de fichier s'il est trop long
    max_length = 100
    return filename[:max_length]








    