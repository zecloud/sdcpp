# Dossier `uitester`

Le dossier `uitester` contient le code pour l'application de test d'interface utilisateur.

## Contenu

- `app.py` : Le fichier principal de l'application de test.
- `Dockerfile` : Le fichier Docker pour construire l'image de l'application.
- `requirements.txt` : Liste des dépendances Python nécessaires pour l'application.

## Instructions pour exécuter le code

1. Construisez l'image Docker :
   ```bash
   docker build -t uitester .
   ```

2. Exécutez le conteneur Docker :
   ```bash
   docker run -p 8000:8000 uitester
   ```
