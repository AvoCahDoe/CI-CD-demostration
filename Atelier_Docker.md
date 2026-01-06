# Atelier CI/CD : Transition vers Docker

Ce guide détaille les étapes pour passer d'un déploiement basé sur un fichier ZIP à l'utilisation de conteneurs Docker standardisés.

## Introduction

Passer d'un simple fichier ZIP à une Image Docker est le standard actuel de l'industrie. Cela garantit que votre application fonctionnera de la même façon sur votre machine, sur le serveur de test et en production.

---

## 🛠️ Ce qui change

Au lieu de créer un fichier zip, notre pipeline va :

1.  Construire une image Docker (l'application + Python + ses dépendances).
2.  Stocker (Push) cette image dans le registre de conteneurs de GitHub (GHCR - GitHub Container Registry).

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

## Étape 2 : Mettre à jour le Pipeline (`main.yml`)

Nous allons modifier le fichier `.github/workflows/main.yml`. Nous gardons le job de test (CI), mais nous remplaçons le job de "build" par un job "docker".

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
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Construction et Push de l'image Docker
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          # ATTENTION : Remplacez 'votre-pseudo' par votre nom d'utilisateur GitHub (en minuscules !)
          tags: ghcr.io/${{ github.actor }}/calculatrice:latest
```

> **ℹ️ Note sur les identifiants :**
> Vous n'avez **pas besoin** de créer ces secrets vous-même :
>
> - `${{ github.actor }}` : C'est automatiquement votre nom d'utilisateur GitHub.
> - `${{ secrets.GITHUB_TOKEN }}` : C'est un mot de passe temporaire unique généré automatiquement par GitHub pour chaque exécution du pipeline. Il permet au pipeline de se connecter à votre compte sans que vous ayez à stocker votre vrai mot de passe.
>
> **⚠️ Important :** Dans la ligne `tags`, assurez-vous que le nom d'utilisateur est en minuscules. La variable `${{ github.actor }}` récupère automatiquement votre pseudo, mais si vous l'écrivez en dur, utilisez des minuscules.

---

## Étape 3 : Vérifier le résultat

1.  Faites un **Commit** de ces changements.
2.  Allez dans l'onglet **Actions** pour voir le déroulement.
3.  Une fois les deux cercles verts (Test et Build-Push), la magie a opéré.

### Où est mon image Docker ?

1.  Retournez sur la page d'accueil de votre dépôt GitHub.
2.  Regardez dans la colonne de droite, vous devriez voir une section **Packages**.
3.  Vous y verrez votre image Docker prête à être téléchargée (`pull`) par n'importe quel serveur.

---

## Résumé de ce que vous avez construit

À chaque modification de code :

- GitHub **vérifie** que vous n'avez rien cassé (Tests).
- Si c'est bon, il **emballe** le tout dans un conteneur sécurisé.
- Il le **met à disposition** dans votre registre privé.
