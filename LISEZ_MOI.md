# DV Pro, copie de secours du registre des copropriétés

Ce dossier contient tout ce qu'il faut pour publier chaque jour, gratuitement, une copie de secours du registre national des copropriétés. DV Pro la lira seulement quand le registre de data.gouv ne répond pas, comme le 02/11/2026.

- `construire_registre.py` : le programme qui télécharge le fichier du jour et prépare la copie, avec seulement les colonnes utiles à DV Pro. Essai sur le fichier du 02/11 : 656 263 copropriétés, 13 469 communes, 265 Mo, moins de 3 minutes.
- `registre.yml` : la tâche quotidienne, à placer dans le dépôt sous `.github/workflows/registre.yml`.
- Ce dépôt ne contient aucune ligne du code de DV Pro, aucune licence, aucun mot de passe. La copie publiée ne contient que des données publiques.

## Ce que vous faites (une seule fois, 10 minutes)
1. Créer un compte gratuit sur github.com, avec votre adresse professionnelle. Choisir un nom de compte court, par exemple `tpfc-dvpro` : il apparaîtra dans l'adresse de la copie.
2. Créer un dépôt **public** nommé exactement `dvpro-secours` (bouton « New repository »), sans rien cocher d'autre.
3. Dans le dépôt, « Add file », puis « Upload files » : déposer `construire_registre.py` et `LISEZ_MOI.md`.
4. « Add file », puis « Create new file » : taper comme nom `.github/workflows/registre.yml`, coller le contenu de `registre.yml`, puis « Commit changes ».
5. « Settings », puis « Pages » : dans « Build and deployment », choisir « Source : GitHub Actions ».
6. Onglet « Actions », « Copie du registre », puis « Run workflow » pour un premier essai (environ 5 minutes).
7. Me donner le nom du compte. Je règle l'adresse dans DV Pro, je vérifie la copie en ligne et je prépare la version à déposer. Le dépôt de DV Pro reste votre décision.

## Ensuite
- La copie se met à jour seule chaque jour vers 10 h 35 (heure de Paris).
- Si le fichier du jour est absent ou incomplet, rien n'est publié : la copie de la veille reste en ligne.
- Le contrôle du matin vérifiera aussi que la copie est à jour.
- Coût : 0 €. GitHub Actions est gratuit pour un dépôt public, et GitHub Pages accepte jusqu'à 1 Go de fichiers et 100 Go de trafic par mois.
