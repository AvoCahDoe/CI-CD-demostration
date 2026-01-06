# Atelier CI/CD : Transition vers Docker

Ce guide détaille les étapes pour passer d'un déploiement basé sur un fichier ZIP à l'utilisation de conteneurs Docker standardisés.

## Introduction

Passer d'un simple fichier ZIP à une Image Docker est le standard actuel de l'industrie. Cela garantit que votre application fonctionnera de la même façon sur votre machine, sur le serveur de test et en production.

---

## 🛠️ Ce qui change

Au lieu de créer un fichier zip, notre pipeline va :

1.  Construire une image Docker (l'application + Python + ses dépendances).
2.  Stocker (Push) cette image dans le registre de conteneurs de GitHub (GHCR) **ET** sur Docker Hub.

---

## Étape 1 : Créer le Dockerfile

Nous devons expliquer à Docker comment construire notre application.

1.  À la racine de votre dépôt, créez un nouveau fichier nommé `Dockerfile` (sans extension).
2.  Collez ce contenu :

```dockerfile
# 1. Image de base : Un Linux léger avec Python installé
FROM python:3.9-slim

# 2. Dossier de travail dans le conteneur
WORKDIR /app

# 3. Copier les fichiers du projet dans le conteneur
COPY . .

# 4. Commande à lancer au démarrage du conteneur
# (Ici on lance juste le script, pour une vraie app web ce serait le serveur)
CMD ["python", "calculatrice.py"]
```

---

## Étape 2 : Préparer les Secrets pour Docker Hub

Pour publier sur Docker Hub, vous devez fournir vos identifiants à GitHub de manière sécurisée.

1.  Allez sur votre dépôt GitHub.
2.  Cliquez sur **Settings** (Paramètres) > **Secrets and variables** > **Actions**.
3.  Cliquez sur **New repository secret** et ajoutez les deux secrets suivants :
    - `DOCKERHUB_USERNAME` : Votre nom d'utilisateur Docker Hub.
    - `DOCKERHUB_TOKEN` : Votre mot de passe Docker Hub ou un Access Token (recommandé).

---

## Étape 3 : Mettre à jour le Pipeline (`main.yml`)

Nous allons modifier le fichier `.github/workflows/main.yml`. Nous ajoutons une étape de connexion à Docker Hub et mettons à jour la liste des tags.

Voici le fichier complet mis à jour :

```yaml
name: CI/CD avec Docker

on: [push]

jobs:
  # JOB 1 : CI (Reste identique)
  test-app:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.9"
      - run: python test_calculatrice.py

  # JOB 2 : CD (Docker)
  build-push-docker:
    needs: test-app # On attend que les tests soient OK
    runs-on: ubuntu-latest

    # Permission nécessaire pour que le pipeline puisse écrire dans le registre GitHub
    permissions:
      contents: read
      packages: write

    steps:
      - name: Récupérer le code
        uses: actions/checkout@v3

      - name: Connexion au registre GitHub (GHCR)
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }} # Votre nom d'utilisateur GitHub (Automatique)
          password: ${{ secrets.GITHUB_TOKEN }} # Token généré automatiquement par GitHub Action (Pas besoin de le créer)

      - name: Connexion à Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Construction et Push de l'image Docker
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.actor }}/calculatrice:latest
            ${{ secrets.DOCKERHUB_USERNAME }}/calculatrice:latest
```

## 📖 Référence : D'où viennent ces variables `${{ ... }}` ?

Voici un tableau récapitulatif pour savoir quoi faire avec chaque variable :

| Variable                                | D'où ça vient ?          | Action requise de votre part                                                        |
| :-------------------------------------- | :----------------------- | :---------------------------------------------------------------------------------- |
| **`${{ github.actor }}`**               | **Automatique** (GitHub) | **Aucune**. C'est votre pseudo GitHub. Le système le remplit tout seul.             |
| **`${{ secrets.GITHUB_TOKEN }}`**       | **Automatique** (GitHub) | **Aucune**. C'est un code secret temporaire créé par GitHub juste pour ce pipeline. |
| **`${{ secrets.DOCKERHUB_USERNAME }}`** | **Vous** (Secret)        | **À CRÉER**. C'est votre identifiant de connexion sur le site Docker Hub.           |
| **`${{ secrets.DOCKERHUB_TOKEN }}`**    | **Vous** (Secret)        | **À CRÉER**. C'est un "Access Token" à générer sur Docker Hub.                      |

### 🔐 Comment obtenir et ajouter les secrets Docker Hub ?

1.  **Récupérer votre Token sur Docker Hub :**

    - Connectez-vous sur [hub.docker.com](https://hub.docker.com).
    - Cliquez sur votre avatar (en haut à droite) -> **My Account**.
    - Allez dans l'onglet **Security**.
    - Cliquez sur le bouton **New Access Token**.
    - Donnez-lui un nom (ex: "GitHub Actions") et validez.
    - **Copiez le code qui s'affiche** (vous ne pourrez plus le revoir !).

2.  **Ajouter les secrets dans GitHub :**
    - Allez sur la page de votre dépôt GitHub.
    - Cliquez sur l'onglet **Settings** (tout à droite).
    - Dans le menu de gauche : **Secrets and variables** -> **Actions**.
    - Cliquez sur le bouton vert **New repository secret**.
    - Ajoutez **`DOCKERHUB_USERNAME`** (votre pseudo ex: `avocahdoe`).
    - Ajoutez **`DOCKERHUB_TOKEN`** (le code copié à l'étape 1).

---

## Étape 4 : Vérifier le résultat

1.  Faites un **Commit** de ces changements.
2.  Allez dans l'onglet **Actions** pour voir le déroulement.
3.  Une fois terminé, vérifiez :
    - Sur GitHub : Section **Packages**.
    - Sur Docker Hub : Votre nouveau dépôt `calculatrice`.

---

## Résumé

Votre pipeline publie maintenant votre application simultanément sur deux registres majeurs (GitHub et Docker Hub), assurant une disponibilité maximale.
