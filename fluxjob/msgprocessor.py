import time
import threading
from azure.storage.queue import QueueClient

class MessageVisibilityManager:
    def __init__(self, connectionstring: str, message_id: str, pop_receipt: str, queuename:str,visibility_timeout: int = 30):
        """
        Initialise le gestionnaire de visibilité du message.

        :param queue_client: Client Azure Queue pour manipuler la file d'attente.
        :param message_id: ID du message à gérer.
        :param pop_receipt: PopReceipt du message pour prolonger la visibilité.
        :param visibility_timeout: Temps en secondes pendant lequel la visibilité du message est étendue.
        """
        self.queue_client = QueueClient.from_connection_string(connectionstring, queuename)
        self.message_id = message_id
        self.pop_receipt = pop_receipt
        self.visibility_timeout = visibility_timeout
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._update_visibility_periodically)

    def start(self):
        """Démarre le thread pour mettre à jour la visibilité du message périodiquement."""
        self.thread.start()

    def stop(self):
        """Arrête le thread de mise à jour de la visibilité proprement."""
        self.stop_event.set()
        self.thread.join()

    def _update_visibility_periodically(self):
        """Méthode interne pour mettre à jour la visibilité du message à intervalles réguliers."""
        while not self.stop_event.is_set():
            time.sleep(self.visibility_timeout / 2)  # Prolonge la visibilité à mi-parcours du délai
            try:
                updated_message = self.queue_client.update_message(
                    self.message_id,
                    self.pop_receipt,
                    visibility_timeout=self.visibility_timeout
                )
                self.pop_receipt = updated_message.pop_receipt  # Met à jour le pop_receipt
                print(f"Visibilité du message {self.message_id} mise à jour avec succès.")
            except Exception as e:
                print(f"Erreur lors de la mise à jour de la visibilité du message {self.message_id} : {e}")
                break

    def delete_message(self):
        """Supprime le message de la file d'attente."""
        try:
            self.queue_client.delete_message(self.message_id, self.pop_receipt)
            print(f"Message {self.message_id} supprimé avec succès.")
        except Exception as e:
            print(f"Erreur lors de la suppression du message {self.message_id} : {e}")
