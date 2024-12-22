from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from io import BytesIO

class BlobManager:
    def __init__(self, connection_string: str, container_name: str):
        """
        Initialise le client Azure Blob Storage avec une chaîne de connexion et un nom de conteneur.
        
        :param connection_string: La chaîne de connexion pour Azure Storage.
        :param container_name: Le nom du conteneur où stocker les blobs.
        """
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)
        
        # Créer le conteneur s'il n'existe pas déjà
        try: 
            if not (self.container_client.exists()):
                self.container_client.create_container(container_name)
        except ResourceExistsError:
            pass  # Le conteneur existe déjà

    def upload_blob(self, blob_name: str, data: bytes):
        """
        Upload un fichier en mémoire dans un blob de manière synchrone.
        
        :param blob_name: Le nom du blob (fichier) à uploader.
        :param data: Le contenu du fichier à uploader sous forme de bytes.
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.upload_blob(data, overwrite=True)
            print(f"Le blob '{blob_name}' a été téléchargé avec succès.")
        except Exception as e:
            print(f"Erreur lors du téléchargement du blob : {e}")

    def download_blob(self, blob_name: str) -> bytes:
        """
        Télécharge un blob depuis Azure Blob Storage et retourne son contenu sous forme de bytes.
        
        :param blob_name: Le nom du blob à télécharger.
        :return: Le contenu du blob sous forme de bytes.
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_data = blob_client.download_blob()
            return blob_data.readall()
        except ResourceNotFoundError:
            print(f"Le blob '{blob_name}' n'existe pas.")
        except Exception as e:
            print(f"Erreur lors du téléchargement du blob : {e}")
        return None

 