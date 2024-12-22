import base64
from azure.storage.queue import QueueServiceClient, QueueMessage
from azure.core.exceptions import ResourceNotFoundError,ResourceExistsError

class QueueManager:
    def __init__(self, connection_string: str, queue_name: str):
        """
        Initialise le client Azure Queue Storage avec une chaîne de connexion et un nom de queue.
        
        :param connection_string: La chaîne de connexion pour Azure Storage.
        :param queue_name: Le nom de la queue où stocker les messages.
        """
        self.queue_service_client = QueueServiceClient.from_connection_string(connection_string)
        self.queue_client = self.queue_service_client.get_queue_client(queue_name)
        
        # Créer la queue si elle n'existe pas déjà
        try:
            self.queue_client.create_queue()
        except ResourceExistsError:
            pass  # La queue existe déjà

    def encode_base64(self, message: str) -> str:
        """
        Encode un message en Base64.
        
        :param message: Le message à encoder.
        :return: Le message encodé en Base64.
        """
        message_bytes = message.encode('utf-8')
        base64_bytes = base64.b64encode(message_bytes)
        return base64_bytes.decode('utf-8')

    def decode_base64(self, encoded_message: str) -> str:
        """
        Décode un message encodé en Base64.
        
        :param encoded_message: Le message encodé en Base64.
        :return: Le message décodé.
        """
        base64_bytes = encoded_message.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        return message_bytes.decode('utf-8')

    def send_message(self, message: str):
        """
        Envoie un message encodé en Base64 dans la queue.
        
        :param message: Le message à envoyer.
        """
        encoded_message = self.encode_base64(message)
        self.queue_client.send_message(encoded_message)
        print(f"Message envoyé : {message}")

    def receive_message(self) -> str:
        """
        Reçoit et décode un message encodé en Base64 depuis la queue.
        
        :return: Le message décodé.
        """
        try:
            messages = self.queue_client.receive_messages(max_messages=1)
            for message in messages:
                decoded_message = self.decode_base64(message.content)
                print(f"Message reçu et décodé : {decoded_message}")
                
                
                
                return decoded_message,message.id,message.pop_receipt,message.dequeue_count
        except ResourceNotFoundError:
            print("Aucun message trouvé dans la queue.")
        except Exception as e:
            print(f"Erreur lors de la réception du message : {e}")
        return None
