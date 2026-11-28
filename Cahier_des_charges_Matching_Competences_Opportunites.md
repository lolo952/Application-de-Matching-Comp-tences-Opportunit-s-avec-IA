# Cahier des charges – Matching Compétences-Opportunités (PFA n°29)

## 1. Contexte et objectifs

L'application propose à une personne les offres d'emploi les plus proches de son profil (compétences, expérience, ville, contrat). Elle repose sur la comparaison du sens des textes par un modèle d'IA multilingue, et non sur une simple recherche de mots identiques.

Projet PFA n°29, « Application de Matching Compétences-Opportunités avec IA », prévu sur 10 semaines. Il est réalisé par une seule personne, bien qu'il soit prévu en binôme.

Objectifs :

- Classer, pour un CV donné, les offres les plus pertinentes.
- Mesurer la qualité du classement avec une métrique reconnue (NDCG@5).
- Fournir une API, une interface web et un lancement par Docker.
- Présenter le travail par un rapport, une démonstration et une vidéo explicative.

### 1.1 Problématique

Les candidats et les recruteurs manipulent beaucoup de textes libres (CV, annonces) qu'il est long de comparer à la main. Une recherche par mots-clés rate les correspondances formulées autrement, et elle ne fonctionne pas telle quelle quand les CV sont en français et les offres en anglais. Le projet répond à la question suivante : comment classer automatiquement des offres d'emploi, pour un profil donné, selon leur proximité avec ses compétences et son expérience ?

### 1.2 Objectifs mesurables

- Proposer jusqu'à 20 offres par requête (5 par défaut), qui respectent la ville (ou la mobilité) et le contrat demandés.
- Obtenir un NDCG@5 supérieur à celui d'un classement aléatoire sur le jeu de test.
- Traiter une requête sans recalculer les données des offres, chargées une seule fois au démarrage.
- Démarrer toute l'application avec une seule commande.
- Documenter le projet : rapport, README et vidéo de démonstration.

## 2. Parties prenantes et utilisateurs

| Acteur | Rôle | Besoin |
| --- | --- | --- |
| Chercheur d'emploi | Utilisateur final : saisit son profil et lit les offres | Obtenir rapidement des offres pertinentes et comprendre pourquoi (compétences communes) |
| Encadrant | Évalue le projet | Un cahier des charges, des tests reproductibles, une démonstration et un rapport |
| Équipe de développement (2 membres) | Conçoit, développe, teste et documente | Un périmètre réaliste, des outils reproductibles (Git, Docker) |
| Recruteur | Publie des offres | Hors périmètre de cette version : les offres viennent d'un jeu de données fixe |

## 3. Périmètre

**Inclus dans le périmètre :**

- Données : CV marocains (en français) et offres d'emploi (en anglais), nettoyés (contacts retirés, doublons supprimés).
- Matching : filtre sur la ville (ou la mobilité) et le contrat, puis classement par similarité sémantique avec un seuil minimum.
- Extraction de compétences par dictionnaire bilingue et score hybride (similarité du sens et compétences communes).
- Évaluation : paires CV ↔ offre notées de 0 à 2, puis mesure du NDCG@5.
- Backend FastAPI, interface web, conteneur Docker.

**Hors périmètre :**

- Elasticsearch.
- Extraction de compétences avec spaCy (dictionnaire utilisé à la place).
- Annotation humaine exhaustive : seul un échantillon d'environ 30 paires sera validé par une personne.

## 4. Données

Le projet utilise deux jeux de données réels liés au marché de l'emploi marocain, issus d'une même publication sur Figshare (I. Khlif, 2025) : des CV de la plateforme emploi.ma et des offres d'emploi publiées sur Kaggle. Un échantillon de chacun est utilisé.

| Jeu | Fichier | Langue | Champs utilisés |
| --- | --- | --- | --- |
| CV | `data/raw/morocco_CV_sampled_4.csv` | Français | ville, mobilité, contrats recherchés, domaines souhaités, compétences, expérience, langues |
| Offres | `data/raw/morocco_jobs_sampled_5.csv` | Anglais | titre, rôle, ville, type de contrat, compétences, description, responsabilités, expérience requise, qualification |

Règles de préparation (script `01_prepare_morocco.py`) :

- Les colonnes personnelles (contacts) ne sont pas conservées.
- Les espaces superflus sont nettoyés, et les identifiants d'offre sont lus comme du texte.
- Les offres en double (même titre, même rôle, même ville, même contrat) sont supprimées.
- Le texte d'un CV est formé des compétences, des domaines souhaités et de l'expérience ; celui d'une offre, du titre, du rôle, des compétences et de la description.
- Les résultats sont écrits au format parquet dans `data/processed/`.

Contrainte : les données brutes et préparées restent hors de GitHub (fichier `.gitignore`) et hors de l'image Docker.

## 5. Architecture et technologies

> **Schéma d'architecture** : Interface web (page HTML + JavaScript) → API FastAPI → Moteur de matching (filtre, similarité sémantique, score de compétences). L'ensemble tourne dans un conteneur Docker ; les données restent hors de l'image et sont montées en lecture seule.

Le profil va de l'interface à l'API, puis au moteur : filtre, similarité du sens, puis score de compétences. Les données restent hors de l'image Docker et sont montées en lecture seule.

- **Langage** : Python (Python 3.14 dans l'image Docker).
- **IA** : `sentence-transformers`, modèle `paraphrase-multilingual-MiniLM-L12-v2`.
- **Données** : `pandas`, `numpy`, `pyarrow` (fichiers parquet).
- **Backend** : FastAPI et uvicorn.
- **Frontend** : page HTML et JavaScript, servie par l'API.
- **Conteneurs** : Docker et Docker Compose.
- **Qualité** : `pytest`, Git et GitHub (branches et Pull Requests).

## 6. Spécification du moteur de matching

Pour un profil donné, le moteur applique les étapes suivantes dans l'ordre.

1. **Entrée** : compétences, expérience, domaine recherché, ville, villes de mobilité, types de contrat et nombre de résultats `k`.
2. **Filtre dur** : seules sont gardées les offres situées dans la ville du profil (ou dans l'une de ses villes de mobilité) et dont le type de contrat correspond (table ci-dessous).
3. **Similarité sémantique** : le profil et chaque offre sont transformés en vecteurs par le modèle multilingue `paraphrase-multilingual-MiniLM-L12-v2`. Les vecteurs sont normalisés, donc leur produit scalaire donne la similarité cosinus. Les offres dont la similarité est inférieure au seuil minimum sont exclues.
4. **Score de compétences** : un dictionnaire bilingue d'environ 150 compétences (variantes françaises et anglaises, sans tenir compte des accents ni des majuscules) repère les compétences du profil et celles de chaque offre. Le score est le poids des compétences de l'offre présentes dans le profil, divisé par le poids total des compétences de l'offre. Une compétence rare pèse plus qu'une compétence fréquente comme `management` (pondération IDF). Une offre sans compétence reconnue obtient 0.
5. **Score final et classement** : les offres sont triées par score décroissant et les `k` premières sont renvoyées.

```latex
\text{score} = (1 - \alpha)\, s_{\text{sem}} + \alpha\, s_{\text{comp}}, \quad \alpha = 0{,}1
```

Correspondance entre le contrat du profil et le type de contrat de l'offre :

| Contrat du profil | Types d'offre acceptés |
| --- | --- |
| CDI | Full-Time |
| CDD | Contract, Temporary |
| Freelance | Contract |
| Stage | Intern |

Paramètres du moteur :

| Paramètre | Valeur par défaut | Rôle |
| --- | --- | --- |
| Seuil minimum de similarité | 0,35 | Exclut les offres trop éloignées du profil |
| Poids des compétences (α) | 0,1 | Part du score de compétences dans le score final |
| Nombre de résultats (`k`) | 5 (de 1 à 20) | Taille de la liste renvoyée |
| Modèle | `paraphrase-multilingual-MiniLM-L12-v2` | Représentation du sens des textes |

## 7. Exigences fonctionnelles

| Réf. | Partie | Exigence |
| --- | --- | --- |
| EF1 | Backend | `GET /health` renvoie l'état de l'API et le nombre d'offres chargées. |
| EF2 | Backend | `POST /match` reçoit un profil : compétences et ville (obligatoires), expérience, domaine, mobilité, contrats, nombre de résultats `k` (1 à 20, 5 par défaut). |
| EF3 | Backend | Seules les offres de la ville (ou des villes de mobilité) et du type de contrat demandés sont proposées. |
| EF4 | Backend | Les offres sont classées par score : 90 % similarité sémantique et 10 % compétences communes. Les offres sous 0,35 de similarité sont exclues. |
| EF5 | Backend | Chaque résultat contient : identifiant, titre, rôle, ville, contrat, score, score sémantique, compétences communes. |
| EF6 | Backend | Un profil invalide (champ obligatoire absent) renvoie une erreur 422. |
| EF7 | Frontend | Un formulaire permet de saisir le profil et de cocher les contrats (CDI, CDD, Freelance, Stage). |
| EF8 | Frontend | Les résultats s'affichent en cartes : titre, rôle, ville, contrat, score en %, compétences communes. |
| EF9 | Frontend | Si aucune offre ne correspond, un message le dit et suggère d'ajouter une ville ou un contrat. |
| EF10 | Frontend | Une erreur de l'API est signalée à l'utilisateur. |

### Cas d'utilisation principaux

1. **Rechercher des offres** : l'utilisateur ouvre la page, remplit son profil, coche ses contrats, lance la recherche et lit les offres classées avec leur score et leurs compétences communes.
2. **Élargir la recherche** : si aucune offre ne correspond, l'utilisateur ajoute des villes de mobilité ou d'autres types de contrat, puis relance la recherche.
3. **Utiliser l'API directement** : un développeur ou un autre service appelle `POST /match` et exploite la réponse JSON.
4. **Vérifier le service** : un opérateur appelle `GET /health` pour savoir si l'API est prête.

## 8. Interface de l'API

L'API est documentée automatiquement par FastAPI à l'adresse `/docs`. La page web est servie à la racine `/`.

| Route | Méthode | Rôle | Réponses |
| --- | --- | --- | --- |
| `/` | GET | Affiche la page web | 200 |
| `/health` | GET | État de l'API et nombre d'offres chargées | 200 |
| `/match` | POST | Classe les offres pour un profil | 200, 422 (profil invalide) |

Champs du profil envoyé à `POST /match` :

| Champ | Type | Obligatoire | Description |
| --- | --- | --- | --- |
| `skills` | texte | Oui | Compétences du profil |
| `experience` | texte | Non | Expérience professionnelle |
| `desired_fields` | texte | Non | Domaines recherchés |
| `city` | texte | Oui | Ville de recherche |
| `mobility` | liste de textes | Non | Autres villes acceptables |
| `contracts` | liste de textes | Oui | Contrats parmi CDI, CDD, Freelance, Stage |
| `k` | entier | Non | Nombre d'offres à renvoyer, de 1 à 20 (5 par défaut) |

## 9. Exigences non fonctionnelles et contraintes

- **Lancement simple** : l'application démarre avec `docker compose up --build`, sans autre installation que Docker.
- **Données personnelles** : les contacts des CV ne sont pas utilisés, et `data/processed/` est exclu de GitHub et de l'image Docker (les données sont montées en lecture seule).
- **Multilinguisme** : des CV en français doivent être comparés à des offres en anglais.
- **Performance** : le moteur charge le modèle et calcule les représentations des offres une seule fois, au démarrage ; ensuite chaque requête ne traite que le CV reçu.
- **Reproductibilité** : versions des bibliothèques fixées dans `requirements.txt`.
- **Travail collaboratif** : une branche par fonctionnalité, fusionnée par Pull Request.
- **Contrainte de ressources** : projet réalisé par une seule personne en 10 semaines.

### Exigences complémentaires

- **Sécurité et confidentialité** : l'application n'enregistre pas les profils saisis ; aucune donnée personnelle de CV n'est publiée sur GitHub ni intégrée à l'image Docker.
- **Maintenabilité** : le code est découpé en modules (préparation des données, matching, compétences, moteur, API), chacun avec une seule responsabilité.
- **Extensibilité** : le dictionnaire de compétences et les paramètres du moteur (seuil, poids, `k`) se modifient sans réécrire le moteur.
- **Portabilité** : l'application fonctionne de la même façon sous Windows et dans Docker.
- **Ergonomie** : l'interface est en français et s'adapte à la largeur de l'écran (ordinateur et téléphone).
- **Fiabilité** : une erreur de l'API ou une liste vide ne bloque pas la page ; un message explique la situation.
- **Documentation** : un fichier README explique l'installation, le lancement et l'utilisation.

## 10. Plan de test

Chaque scénario décrit l'entrée et le résultat attendu. Les scénarios 1, 3, 4, 5, 7 et 8 seront automatisés avec `pytest` dans le dossier `tests/`.

| N° | Scénario | Entrée | Résultat attendu |
| --- | --- | --- | --- |
| 1 | Santé de l'API | `GET /health` | `status: ok` et le nombre d'offres |
| 2 | Profil informatique | Python SQL React, Rabat, CDI et CDD | Offres de base de données ou de développement, avec `python` et `sql` en compétences communes |
| 3 | Champ obligatoire absent | Profil sans `skills` | Erreur 422 |
| 4 | Ville sans offre | Ville absente du jeu de données | Liste vide, message dans l'interface |
| 5 | Filtre de contrat | Stage uniquement | Seulement des offres de type Intern |
| 6 | Mobilité | Rabat, mobilité Tanger et Casablanca | Offres de ces trois villes |
| 7 | Extraction des compétences | « Java et React » | `java` et `react` |
| 8 | Nombre de résultats | `k` = 3 | Au plus 3 offres |
| 9 | Interface | Formulaire rempli, clic sur « Trouver des offres » | Cartes avec score et compétences communes |
| 10 | Docker | `docker compose up --build` | Application accessible sur le port 8000, mêmes résultats qu'en local |
| 11 | Évaluation | `05_hybrid_eval.py` | NDCG@5 calculé, supérieur à celui d'un classement aléatoire |

Critère d'évaluation : le NDCG@5 du moteur doit dépasser celui d'un classement aléatoire. Les notes d'annotation seront validées par une personne sur un échantillon d'environ 30 paires.

## 11. Test de la prédiction (matching CV ↔ offres)

Objectif : vérifier que, pour un CV donné, les offres proposées en tête sont bien les plus pertinentes.

- **Jeu de test** : 30 CV tirés du jeu de données, avec pour chacun 10 offres candidates (les mieux classées après le filtre ville et contrat), présentées dans un ordre aléatoire et sans les scores du modèle.
- **Annotation** : chaque paire est notée 0 (autre métier), 1 (même domaine ou poste voisin) ou 2 (métier et compétences correspondent), sur le contenu uniquement.
- **Métriques** : NDCG@5 (métrique principale) et part des offres notées 1 ou 2 parmi les 5 premières.
- **Références de comparaison** : classement aléatoire, similarité sémantique seule, compétences seules, score hybride (poids des compétences de 0 à 1 par pas de 0,1).
- **Critères d'acceptation** : le NDCG@5 du moteur dépasse celui du classement aléatoire ; le poids des compétences et le seuil minimum sont choisis d'après ces mesures.
- **Cas limites** : CV sans compétence reconnue (classement par similarité seule), ville sans offre (liste vide), profil très court (résultat sans erreur).
- **Validité** : les notes sont validées par une personne sur un échantillon d'environ 30 paires ; les limites (30 CV, annotateur unique) sont indiquées dans le rapport.

## 12. Planning prévisionnel (10 semaines)

| Phase | Semaines | Travaux | Livrable |
| --- | --- | --- | --- |
| 1. Cadrage | 1 | Cadrage du sujet, choix des données, mise en place du dépôt GitHub et des branches | Dépôt GitHub, fiche de cadrage |
| 2. Données | 2 et 3 | Exploration et préparation des données | Fichiers préparés (parquet) |
| 3. Matching de référence | 3 et 4 | Filtre ville et contrat, similarité sémantique | Script de matching |
| 4. Évaluation | 4 et 5 | Jeu de test, annotation, mesure du NDCG@5 | Feuille d'annotation, mesure du NDCG@5 |
| 5. Compétences | 6 | Extraction de compétences, score hybride, réglage du poids et du seuil | Dictionnaire de compétences, score hybride |
| 6. API | 7 | Développement de l'API FastAPI | API (`/match`, `/health`) |
| 7. Interface | 8 | Développement de l'interface web | Page web |
| 8. Docker et tests | 9 | Conteneurisation, tests automatisés | `Dockerfile`, `docker-compose.yml`, tests `pytest` |
| 9. Finalisation | 10 | Rapport, README, vidéo et démonstration | Rapport, README, vidéo |

## 13. Risques et mesures prévues

| Risque | Conséquence | Mesure |
| --- | --- | --- |
| Peu d'offres dans une ville | Liste vide | Villes de mobilité, message explicatif, ajout d'autres types de contrat |
| Offres peu pertinentes (jeu de données générique) | Résultats hors sujet | Seuil minimum de similarité ; piste d'amélioration : enrichir le jeu d'offres |
| Annotation subjective, annotateur unique | Mesure de qualité peu fiable | Validation humaine d'un échantillon, limites indiquées dans le rapport |
| Compétence absente du dictionnaire | Compétence non détectée | Classement par similarité sémantique, enrichissement du dictionnaire |
| Projet prévu pour deux personnes, réalisé par une seule | Retard | Périmètre réduit (Elasticsearch reporté), priorités claires |
| Fuite de données personnelles | Atteinte à la vie privée | Contacts retirés, données hors de GitHub et de l'image Docker |
| Premier démarrage de Docker long | Démonstration retardée | Lancer et vérifier l'application avant la démonstration |

## 14. Glossaire

| Terme | Définition |
| --- | --- |
| Matching | Mise en correspondance d'un profil et d'offres d'emploi |
| Similarité sémantique | Mesure de la proximité de sens entre deux textes, entre 0 et 1 dans ce projet |
| Vecteur (embedding) | Suite de nombres qui représente le sens d'un texte |
| Similarité cosinus | Mesure de l'angle entre deux vecteurs ; plus il est petit, plus les textes se ressemblent |
| Filtre dur | Critère obligatoire (ville, contrat) qui élimine les offres avant le classement |
| Score hybride | Mélange de la similarité sémantique et du score de compétences |
| IDF | Pondération qui donne plus de poids aux compétences rares |
| NDCG@5 | Mesure entre 0 et 1 qui vérifie si les offres les plus pertinentes sont placées en tête des 5 premières |
| API | Programme qui reçoit des requêtes et renvoie des réponses à d'autres programmes |
| Docker | Outil qui emballe l'application pour la lancer de la même façon sur n'importe quel ordinateur |
