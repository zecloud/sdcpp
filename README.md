# SDCpp: Stable Diffusion avec Azure Container Apps Serverless GPU

Bienvenue dans le dépôt **SDCpp**. Ce projet utilise [stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp) basé sur [ggml](https://github.com/ggerganov/ggml), qui fonctionne de la même façon que [llama.cpp](https://github.com/ggerganov/llama.cpp) et ses bindings Python via [stable-diffusion-cpp-python](https://github.com/william-murray1204/stable-diffusion-cpp-python) pour offrir une solution performante et extensible de génération d'images basée sur Stable Diffusion et FLUX. Le tout est empaqueté dans un conteneur Docker déployable sur **Azure Container Apps** avec support GPU sans serveur.

---

## 🚀 Fonctionnalités

1. **Stable Diffusion et FLUX** : Génération d'images via Stable Diffusion (SD1.x, SD2.x, SDXL, SD3.5) et FLUX.
2. **Bindings Python** : Utilisation simplifiée grâce aux bindings Python pour `stable-diffusion.cpp`.
3. **Conteneur Serverless** : Conteneur prêt à être déployé sur Azure Container Apps avec GPU sans serveur.
4. **Optimisation GPU** : Support CUDA, Vulkan, SYCL et d'autres backends pour accélérer les performances GPU.
5. **Personnalisation avancée** : Intégration LoRA, PhotoMaker, et prise en charge des modèles personnalisés.

---

## 🛠️ Prérequis

1. **Environnement local** :
   - Python 3.8+
   - Docker
   - Azure CLI installé et configuré avec un abonnement.

2. **Accès aux modèles** : Téléchargez les poids nécessaires pour Stable Diffusion et FLUX :
   - [Weights pour Stable Diffusion](https://huggingface.co/stabilityai)
   - [Weights pour FLUX](https://huggingface.co/leejet/FLUX.1-dev-gguf)
   - VAE, CLIP et T5XXL pour FLUX :
     - [vae.safetensors](https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/ae.safetensors)
     - [clip_l.safetensors](https://huggingface.co/comfyanonymous/flux_text_encoders/blob/main/clip_l.safetensors)
     - [t5xxl_fp16.safetensors](https://huggingface.co/comfyanonymous/flux_text_encoders/blob/main/t5xxl_fp16.safetensors)

---

## 📦 Installation

1. Clonez ce dépôt ainsi que ses dépendances :
   ```bash
   git clone https://github.com/zecloud/sdcpp.git
   ```


2. en local Construisez l'image Docker :
   ```bash
   docker build -t sdcpp .
   ```

---

---

### 🏗️ Construire et Pusher l'Image Docker avec Azure Container Registry (ACR)

Cette section explique comment construire l'image Docker pour votre application et la pousser vers un **Azure Container Registry (ACR)**.

#### Étape 1 : Créer un Azure Container Registry

Créez un registre Azure pour stocker vos images Docker.

```bash
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name <ACR_NAME> \
  --sku Basic \
  --admin-enabled true
```

- Remplacez `<ACR_NAME>` par le nom de votre registre.
- La commande retourne les détails du registre si elle réussit.

#### Étape 2 : Connectez-vous à votre registre ACR

Connectez votre terminal au registre ACR.

```bash
az acr login --name <ACR_NAME>
```

#### Étape 3 : Construire l'image Docker

Utilisez la commande `docker build` pour construire l'image.

```bash
az acr build -t <ACR_NAME>.azurecr.io/<IMAGE_NAME>:<TAG> -r <ACR_NAME> .
```

- **`<ACR_NAME>`** : Nom de votre registre ACR (défini à l'étape 1).
- **`<IMAGE_NAME>`** : Nom de l'image Docker.
- **`<TAG>`** : Balise (par exemple, `latest` ou une version spécifique).


#### Étape 4 : Vérifier l'image dans le registre

Listez les dépôts disponibles dans votre registre pour confirmer que l'image a bien été poussée.

```bash
az acr repository list --name <ACR_NAME> --output table
```

Vous devriez voir votre image répertoriée.

---

#### Exemple Complet

Voici un exemple complet avec des valeurs spécifiques :
```bash
RESOURCE_GROUP="sdcpp-resource-group"
ACR_NAME="sdcppregistry"
IMAGE_NAME="sdcpp-image"
TAG="v1.0"

# Créer le registre
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Connexion au registre
az acr login --name $ACR_NAME

# Construire l'image
docker build -t $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG .

# Pusher l'image
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG

# Vérifier l'image
az acr repository list --name $ACR_NAME --output table
```

---


#### Étape Suivante

Vous avez l'image de base construite, maintenant construisez une des images docker dans les sous dossiers basé sur cette image de base docker, répétez les mêmes étapes pour construire une de ces images. 

Une fois que l'image est dans **Azure Container Registry**, utilisez-la dans votre déploiement Azure Container Apps en remplaçant `mcr.microsoft.com/k8se/gpu-quickstart:latest` par `<ACR_NAME>.azurecr.io/<IMAGE_NAME>:<TAG>` dans les commandes de déploiement.



## 🌐 Déploiement sur Azure Container Apps avec GPU Serverless

Suivez les étapes ci-dessous pour déployer votre conteneur sur Azure Container Apps avec des GPU NC8as-T4 sans serveur.

### Étape 1 : Définir les variables d'environnement

Définissez les variables suivantes dans votre terminal. Remplacez `<PLACEHOLDERS>` par vos valeurs spécifiques.

```bash
RESOURCE_GROUP="<RESOURCE_GROUP>"
ENVIRONMENT_NAME="<ENVIRONMENT_NAME>"
LOCATION="swedencentral"
CONTAINER_APP_NAME="<CONTAINER_APP_NAME>"
CONTAINER_IMAGE="mcr.microsoft.com/k8se/gpu-quickstart:latest"
WORKLOAD_PROFILE_NAME="NC8as-T4"
WORKLOAD_PROFILE_TYPE="Consumption-GPU-NC8as-T4"
```

### Étape 2 : Créer les ressources

1. **Créer le groupe de ressources :**

   Exécutez la commande suivante pour créer un groupe de ressources. Cela devrait retourner `Succeeded`.

   ```bash
   az group create \
     --name $RESOURCE_GROUP \
     --location $LOCATION \
     --query "properties.provisioningState"
   ```

2. **Créer un environnement Container Apps :**

   Créez un environnement pour héberger votre conteneur. Cela devrait retourner `Succeeded`.

   ```bash
   az containerapp env create \
     --name $ENVIRONMENT_NAME \
     --resource-group $RESOURCE_GROUP \
     --location "$LOCATION" \
     --query "properties.provisioningState"
   ```

3. **Ajouter un profil de charge de travail GPU :**

   Ajoutez un profil de charge de travail GPU à votre environnement Container Apps.

   ```bash
   az containerapp env workload-profile add \
     --name $ENVIRONMENT_NAME \
     --resource-group $RESOURCE_GROUP \
     --workload-profile-name $WORKLOAD_PROFILE_NAME \
     --workload-profile-type $WORKLOAD_PROFILE_TYPE
   ```

4. **Créer l'application Container Apps :**

   Créez votre application en spécifiant l'image du conteneur, les ressources GPU et les paramètres d'entrée. Cette commande retournera l'URL de l'application.

   ```bash
   az containerapp create \
     --name $CONTAINER_APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --environment $ENVIRONMENT_NAME \
     --image $CONTAINER_IMAGE \
     --target-port 80 \
     --ingress external \
     --cpu 8.0 \
     --memory 20.0Gi \
     --workload-profile-name $WORKLOAD_PROFILE_NAME \
     --query properties.configuration.ingress.fqdn
   ```

### Étape 3 : Accéder à votre application

Une fois l'application déployée, la commande précédente vous fournira l'URL publique pour accéder à votre application. Vous pouvez ouvrir cette URL dans un navigateur pour vérifier que votre application fonctionne correctement.

---

Si vous avez besoin de plus d'aide avec cette configuration ou si des étapes supplémentaires sont nécessaires pour votre cas d'utilisation spécifique, faites-le moi savoir !


## 🤝 Contribution

Les contributions sont les bienvenues ! Si vous souhaitez contribuer :

1. Forkez ce dépôt.
2. Créez une branche pour vos modifications :
   ```bash
   git checkout -b feature/nom-de-la-fonctionnalité
   ```
3. Soumettez une pull request.

---

## 📧 Contact

Pour toute question ou suggestion, veuillez ouvrir une issue ou contacter [@zecloud](https://github.com/zecloud).

---

## 📜 Licence

Ce projet est sous licence MIT. Consultez le fichier [LICENSE](./LICENSE) pour plus de détails.

---

Ce README est basé sur la documentation des projets intégrés et inclut des instructions spécifiques pour le déploiement sur Azure Container Apps. Si vous avez besoin d'ajouter des informations spécifiques, faites-le moi savoir !

---

## 📂 Structure du projet

Le projet est organisé en plusieurs sous-dossiers, chacun ayant un rôle spécifique. Voici un aperçu de la structure globale du projet :

- `chainlit/` : Contient le code pour l'application Chainlit.
- `dapr/publisher/` : Contient le code pour le service de publication Dapr.
- `dapr/subscriber/` : Contient le code pour le service de souscription Dapr.
- `fluxjob/` : Contient le code pour le traitement des tâches de flux.
- `uitester/` : Contient le code pour l'application de test d'interface utilisateur.

---

## 📁 Dossier `chainlit`

Le dossier `chainlit` contient le code pour l'application Chainlit.

### Contenu

- `app.py` : Le fichier principal de l'application Chainlit.
- `Dockerfile` : Le fichier Docker pour construire l'image de l'application.
- `infraaca.sh` : Script pour déployer l'application sur Azure Container Apps.
- `requirements.txt` : Liste des dépendances Python nécessaires pour l'application.

### Instructions pour exécuter le code

1. Construisez l'image Docker :
   ```bash
   docker build -t chainlit .
   ```

2. Exécutez le conteneur Docker :
   ```bash
   docker run -p 8000:8000 chainlit
   ```

---

## 📁 Dossier `dapr/publisher`

Le dossier `dapr/publisher` contient le code pour le service de publication Dapr.

### Contenu

- `app.py` : Le fichier principal du service de publication.
- `Dockerfile` : Le fichier Docker pour construire l'image du service.
- `infraaca.sh` : Script pour déployer le service sur Azure Container Apps.
- `requirements.txt` : Liste des dépendances Python nécessaires pour le service.

### Instructions pour exécuter le code

1. Construisez l'image Docker :
   ```bash
   docker build -t dapr-publisher .
   ```

2. Exécutez le conteneur Docker :
   ```bash
   docker run -p 8000:8000 dapr-publisher
   ```

---

## 📁 Dossier `dapr/subscriber`

Le dossier `dapr/subscriber` contient le code pour le service de souscription Dapr.

### Contenu

- `app.py` : Le fichier principal du service de souscription.
- `Dockerfile` : Le fichier Docker pour construire l'image du service.
- `infraaca.sh` : Script pour déployer le service sur Azure Container Apps.
- `requirements.txt` : Liste des dépendances Python nécessaires pour le service.
- `pubsub.yaml` : Configuration Pub/Sub pour Dapr.
- `statestore.yaml` : Configuration du magasin d'état pour Dapr.

### Instructions pour exécuter le code

1. Construisez l'image Docker :
   ```bash
   docker build -t dapr-subscriber .
   ```

2. Exécutez le conteneur Docker :
   ```bash
   docker run dapr-subscriber
   ```

---

## 📁 Dossier `fluxjob`

Le dossier `fluxjob` contient le code pour le traitement des tâches de flux.

### Contenu

- `blockprocessor.py` : Gestionnaire de blobs Azure.
- `Dockerfile` : Le fichier Docker pour construire l'image du traitement des tâches.
- `job.py` : Le fichier principal pour le traitement des tâches.
- `msgprocessor.py` : Gestionnaire de visibilité des messages.
- `queueprocessor.py` : Gestionnaire de file d'attente Azure.
- `requirements.txt` : Liste des dépendances Python nécessaires pour le traitement des tâches.

### Instructions pour exécuter le code

1. Construisez l'image Docker :
   ```bash
   docker build -t fluxjob .
   ```

2. Exécutez le conteneur Docker :
   ```bash
   docker run fluxjob
   ```

---

## 📁 Dossier `uitester`

Le dossier `uitester` contient le code pour l'application de test d'interface utilisateur.

### Contenu

- `app.py` : Le fichier principal de l'application de test.
- `Dockerfile` : Le fichier Docker pour construire l'image de l'application.
- `requirements.txt` : Liste des dépendances Python nécessaires pour l'application.

### Instructions pour exécuter le code

1. Construisez l'image Docker :
   ```bash
   docker build -t uitester .
   ```

2. Exécutez le conteneur Docker :
   ```bash
   docker run -p 8000:8000 uitester
   ```
