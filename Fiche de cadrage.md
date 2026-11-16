# Fiche de suivi des projets agents IA
## Master • Présentation de l’avancement et plan de correction

**Groupe :** 3  **Projet n :** 29 **Date :** 15/11/2026 
**Intitulé du projet :** Application de Matching Compétences-Opportunités avec IA
**Membres :** Leila Souiri , Marwa Ouabaid
**Jalon examiné :** __________________ **Prochain point :** __________________


---

# 1. Bilan et périmètre

## 1. Quel problème métier traitez-vous, pour quel utilisateur et avec quel résultat attendu ?

Notre projet consiste à développer une application de matching entre les profils des candidats et les offres d'emploi. Les candidats doivent souvent consulter plusieurs offres pour trouver celles qui correspondent à leurs compétences et à leur expérience.
Notre application permettra au candidat de fournir son CV, d'extraire ses compétences et de recevoir un classement des offres les plus adaptées à son profil.
Le résultat attendu est de proposer des offres pertinentes, classées selon un score de correspondance entre les compétences du candidat et celles demandées dans chaque offre.

**Critère de réussite mesurable :** comparer notre solution à une méthode de référence simple et mesurer la pertinence des cinq premières offres avec la métrique `nDCG@5`.

## 2. Quel périmètre MVP avez-vous retenu et quelles fonctions avez-vous reportées ?


Le MVP comprendra :

- L'importation d'un CV.
- L'extraction des compétences et des expériences.
- Le chargement d'offres d'emploi réelles.
- Le calcul d'un score de similarité entre le profil et chaque offre.
- Le classement des offres les plus pertinentes.
- L'affichage des résultats avec une explication simple du matching.
Les fonctionnalités reportées pourront être la création de comptes complets, les notifications, les recommandations de formations, l'intégration avec des plateformes de recrutement et le contrôle avancé de l'équité.
Nous allons d'abord privilégier une application fonctionnelle avec des résultats reproductibles avant d'ajouter des fonctionnalités secondaires.


## 3. Qu'aviez-vous prévu depuis le dernier point et qu'avez-vous réellement terminé ?


- **Prévu :** trouver des CV réels et des offres d'emploi réelles, vérifier les licences, nettoyer les données et définir une première méthode de classement.
- **En cours :** renseigner uniquement les tâches sur lesquelles nous avons effectivement travaillé.
- **Terminé :** renseigner uniquement les tâches terminées et vérifiables.
- **Bloqué :** indiquer les éventuels problèmes d'accès aux données, de format ou de développement.


## 4. Que peut-on exécuter aujourd'hui sans intervention manuelle cachée ?

Nous devons démontrer un scénario complet dans lequel l'application reçoit un CV, extrait les compétences, compare le profil aux offres enregistrées et affiche les offres classées.
Le scénario doit pouvoir être relancé avec les mêmes données et sans modifier manuellement les résultats entre les étapes.
Si le pipeline complet n'est pas encore disponible, nous présenterons uniquement les étapes qui fonctionnent et expliquerons ce qu'il reste à intégrer.

---

# 2. Données et architecture

## 5. Quel dataset ou corpus utilisez-vous exactement et comment y accède-t-on ?

Nous recherchons deux jeux de données réels et complémentaires : un corpus de CV de candidats et un corpus d'offres d'emploi. Nous privilégions les profils anonymisés et les données dont les conditions d'utilisation sont documentées.

Pistes identifiées :

- **CV candidats :** [CareerCorpus sur Mendeley Data](https://data.mendeley.com/datasets/wzzwn37gmd/1). La fiche annonce 302 CV anonymisés et annotés répartis en six catégories professionnelles, avec une licence CC BY 4.0. Les catégories ne sont pas centrées sur les métiers informatiques : il faut vérifier si le corpus convient au périmètre retenu.
- **Offres d'emploi :** [Global Job Postings Multi-ATS sur Hugging Face](https://huggingface.co/datasets/NextGig-Rocks/global-job-postings-multi-ats). La fiche annonce environ 113 000 annonces et indique une licence CC BY 4.0. Il faut vérifier la version exacte, la provenance des données et les conditions de réutilisation avant de les intégrer.
- **Autre piste pour les offres informatiques :** [Recruitment dataset — job descriptions in English sur Hugging Face](https://huggingface.co/datasets/Lucas44/recruitment-dataset-job-descriptions-english). La fiche annonce environ 142 000 offres publiées entre 2020 et 2023 et indique une licence MIT. Vérifier que cette licence s'applique bien aux données originales et pas seulement à la structure du dataset.

Ces liens sont des pistes de recherche et ne signifient pas que les données ont déjà été téléchargées ou validées. Nous choisirons les corpus définitifs après vérification de leur compatibilité et de leurs licences.

## 6. Les données couvrent-elles réellement le problème posé ? Que simulez-vous ?

Les offres réelles permettront d'analyser les compétences demandées par les employeurs. Les CV permettront d'extraire les compétences, les expériences et les formations des candidats.
Nous vérifierons que les deux corpus contiennent suffisamment de profils et de postes dans des domaines comparables, notamment l'informatique, la data et l'intelligence artificielle.
Nous ne supposerons pas qu'un CV correspond à une offre simplement parce qu'ils proviennent du même domaine. Pour évaluer la pertinence du classement, nous préparerons un jeu de test avec des correspondances annotées manuellement.
Les correspondances de référence utilisées pour l'évaluation seront annotées par notre groupe et ne seront pas présentées comme des décisions réelles de recrutement.



## 7. Comment avez-vous nettoyé, annoté et séparé les données sans fuite ?

Le pipeline de préparation prévu comporte les étapes suivantes :

1. Supprimer les lignes vides et les enregistrements inutilisables.
2. Normaliser les textes, les espaces, les accents et les variantes d'écriture des compétences.
3. Détecter et supprimer les doublons de CV et d'offres.
4. Extraire les compétences des descriptions et des profils.
5. Annoter un échantillon de correspondances entre candidats et offres pour évaluer le classement.
6. Séparer les données d'évaluation de celles utilisées pour développer ou ajuster la méthode.

Pour éviter les fuites de données, les doublons d'un même profil ou d'une même offre ne devront pas se retrouver dans plusieurs ensembles. Si nous entraînons un modèle, nous documenterons aussi les règles de séparation entre entraînement, validation et test.

## 8. Quelle insuffisance des données risque de fausser votre conclusion ?

Les principales limites possibles sont :

- Les CV et les offres peuvent ne pas concerner les mêmes métiers.
- Les offres peuvent être anciennes ou déjà clôturées.
- Les compétences peuvent être exprimées avec des synonymes ou dans plusieurs langues.
- Les CV publiés publiquement ne représentent pas nécessairement tous les profils de candidats.
- Les annotations de pertinence réalisées par notre groupe peuvent être subjectives.

Pour limiter ces effets, nous sélectionnerons des métiers comparables, conserverons la date et la source des offres, normaliserons les compétences et documenterons les critères d'annotation.
Nous préciserons que notre évaluation mesure la pertinence du matching sur notre échantillon, et non la capacité à prédire une embauche réelle.

## 9. Quels composants fonctionnent et comment échangent-ils les données ?

- **React :** interface permettant d'importer un CV et de consulter les offres recommandées.
- **FastAPI :** backend qui reçoit les demandes, traite les données et expose les résultats.
- **spaCy :** traitement du texte et extraction des informations utiles.
- **Sentence Transformers :** calcul de similarité sémantique entre le profil et les offres.
- **PostgreSQL :** stockage des candidats, des offres, des compétences extraites et des résultats de matching.

Le fonctionnement prévu est le suivant :

1. Le candidat importe un CV.
2. Le backend extrait et normalise les compétences.
3. Le système compare le profil aux offres disponibles.
4. Il calcule un score et classe les offres.
5. L'interface affiche les résultats et les principales raisons du classement.

## 10. Pourquoi avez-vous choisi ces frameworks plutôt qu'une solution plus simple ?

Nous avons retenu ces technologies en fonction des besoins du projet :

- **React** pour créer une interface interactive.
- **FastAPI** pour développer rapidement une API Python et faciliter les tests.
- **spaCy** pour le traitement linguistique et l'extraction d'informations dans les CV et les offres.
- **Sentence Transformers** pour comparer le sens des textes, au-delà de la simple présence de mots identiques.
- **PostgreSQL** pour stocker les profils, les offres et les résultats de manière structurée.

Nous commencerons par une méthode de référence simple, basée sur la correspondance entre les compétences. Nous comparerons ensuite cette méthode avec la similarité sémantique.
Cette comparaison permettra de vérifier si la complexité supplémentaire apporte réellement une amélioration. Nous n'ajouterons Elasticsearch que si un besoin concret de recherche à grande échelle est démontré.

## 11. Comment gérez-vous l'état, la mémoire, les erreurs et les reprises ?

Notre système conservera dans PostgreSQL les informations nécessaires au traitement : identifiant du candidat, CV traité, compétences extraites, offres disponibles et résultats du matching.

Nous prévoyons les mécanismes suivants :

- Validation du format et du contenu des CV importés.
- Gestion des erreurs lorsqu'un fichier est illisible ou incomplet.
- Vérification de la disponibilité des offres avant le classement.
- Journalisation des erreurs techniques sans enregistrer inutilement de données personnelles.
- Possibilité de relancer un traitement échoué sans créer de doublons.
- Conservation des scores et des versions de traitement pour rendre les résultats vérifiables.

Pour le MVP, une mémoire conversationnelle ou un système complexe d'agents persistants n'est pas nécessaire au matching de base. Si l'enseignant exige explicitement un agent IA, nous ajouterons une orchestration contrôlée et documenterons ses décisions, les outils appelés et les erreurs traitées.

---

## Correction prioritaire sur les données ou la conception

Notre priorité est de valider les deux bases de données avant de développer le système de matching. Nous devons confirmer que les CV et les offres sont réels, accessibles, suffisamment compatibles et utilisables dans le cadre du projet.

Ensuite, nous préparerons un échantillon propre, une méthode de référence par mots-clés et un protocole d'évaluation reproductible. Nous comparerons cette méthode au matching sémantique à l'aide de `nDCG@5`.

Nous vérifierons également si l'enseignant exige un véritable agent IA ou si une architecture NLP avec orchestration contrôlée est suffisante.

**Échéance proposée :** fin de la semaine consacrée à la validation des données et à l'architecture, conformément au planning du projet.

---

