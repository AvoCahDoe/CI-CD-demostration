# 1. Image de base : Un Linux léger avec Python installé
FROM python:3.9-slim

# 2. Dossier de travail dans le conteneur
WORKDIR /app

# 3. Copier les fichiers du projet dans le conteneur
COPY . .

# 4. Commande à lancer au démarrage du conteneur
# (Ici on lance juste le script, pour une vraie app web ce serait le serveur)
CMD ["python", "calculatrice.py"]
