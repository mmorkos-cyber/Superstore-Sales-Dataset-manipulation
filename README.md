# Superstore Sales — Prévision des ventes

Projet de fin de formation **Développeur en Intelligence Artificielle** (Simplon Montpellier).

À partir du jeu de données [Superstore Sales](https://www.kaggle.com/datasets/ishanshrivastava28/superstore-sales), ce projet met en place un pipeline de données complet : extraction des données brutes, modélisation dans une base relationnelle puis dans un modèle en étoile, entraînement d'un modèle de prévision des ventes, et tableau de bord interactif.

**Problématique** : peut-on prévoir le chiffre d'affaires mensuel de Superstore, par catégorie de produit et par région, à partir de l'historique de ses ventes ?

La problématique, les hypothèses et l'analyse des résultats sont détaillées dans [`docs/problematique.md`](docs/problematique.md).

---

## Sommaire

- [Pipeline](#pipeline)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Modélisation des données](#modélisation-des-données)
- [Modèle de prévision](#modèle-de-prévision)
- [Tableau de bord](#tableau-de-bord)
- [Technologies](#technologies)
- [Défis et badges](#défis-et-badges)

---

## Pipeline

```
Kaggle (CSV)
    │  Étape 1 : téléchargement et extraction
    ▼
data/raw/Superstore.csv
    │  Étape 2 : ETL relationnel (nettoyage, normalisation)
    ▼
Base relationnelle (DuckDB) — 6 tables normalisées
    │  Étape 3 : ETL analytique (dénormalisation, dimension date)
    ▼
Base analytique (DuckDB) — modèle en étoile
    │  Étape 4 : entraînement
    ▼
Modèle de prévision
    │  Étape 5 : lancement du tableau de bord
    ▼
Tableau de bord Streamlit (lit la base analytique et le modèle)
```

1. **Téléchargement** : le jeu de données est téléchargé depuis Kaggle et extrait dans `data/raw/`. L'étape est ignorée si les fichiers sont déjà présents.
2. **ETL relationnel** : lecture du CSV, conversion des dates, correction des codes postaux, découpage en 6 tables normalisées et chargement avec clés primaires et étrangères. L'étape est ignorée si la base est déjà remplie.
3. **ETL analytique** : construction du modèle en étoile à partir de la base relationnelle, avec une dimension date continue et le calcul du délai d'expédition.
4. **Entraînement** : agrégation mensuelle des ventes, comparaison de deux modèles et sauvegarde du meilleur.
5. **Tableau de bord** : lancement de l'application Streamlit dans le navigateur.

---

## Structure du projet

```
Superstore-Sales-Dataset-manipulation/
├── dashboard/
│   ├── app.py                         # Point d'entrée du tableau de bord Streamlit
│   ├── db.py                          # Connexion à la base analytique
│   └── onglets/                       # Un fichier par onglet du tableau de bord
│       ├── vue_kpi.py
│       ├── dashboard_clients.py
│       ├── dashboard_commerciale.py
│       ├── dashboard_geographique.py
│       ├── dashboard_logistique.py
│       ├── dashboard_rentabilite.py
│       ├── dashboard_temporelle.py
│       └── dashboard_prevision.py
├── data/
│   ├── raw/                           # Données brutes (CSV téléchargé)
│   ├── db/                            # Bases DuckDB relationnelle et analytique
│   └── modeles/                       # Modèle entraîné et rapport d'entraînement
├── docs/
│   ├── problematique.md               # Problématique, hypothèses et résultats
│   ├── Dictionnaire_des_données.md    # Description de chaque table et colonne
│   ├── MCD_Superstore.loo             # Source Looping du MCD
│   ├── MCD_superstore.png             # Modèle conceptuel de données
│   ├── MLD_superstore.png             # Modèle logique de données
│   └── diagramme_en_etoile_base_analytique.png
├── ETL_relationnelle/
│   ├── extraction.py                  # Lecture du CSV
│   ├── transform.py                   # Nettoyage et découpage en tables
│   └── load.py                        # Création et alimentation de la base relationnelle
├── ETL_analytique/
│   ├── extraction_analytique.py       # Lecture de la base relationnelle
│   ├── transform_analytique.py        # Construction des dimensions et de la table de faits
│   └── load_analytique.py             # Création et alimentation du modèle en étoile
├── ML/
│   ├── exploration.py                 # Chargement des données et matrice de corrélation
│   └── entrainement.py                # Entraînement, évaluation et sauvegarde du modèle
├── tests/
│   ├── test_etl_relationnelle.py      # Tests de la base relationnelle
│   ├── test_etl_analytique.py         # Tests du modèle en étoile
│   └── test_modele.py                 # Tests du modèle de prévision
├── utils/
│   ├── dl_fichier_raw.py              # Téléchargement du jeu de données
│   └── logger.py                      # Configuration des logs
├── logs/                              # Fichiers de logs des erreurs
├── main.py                            # Lance le pipeline, les tests puis le tableau de bord
├── requirements.txt
└── README.md
```

---

## Installation

**Prérequis** : Python 3.12 ou supérieur.

1. Cloner le dépôt :

```bash
git clone https://github.com/mmorkos-cyber/Superstore-Sales-Dataset-manipulation.git
cd Superstore-Sales-Dataset-manipulation
```

2. Créer et activer un environnement virtuel (recommandé) :

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
```

3. Installer les dépendances :

```bash
python -m pip install -r requirements.txt
```

Aucune clé d'API Kaggle n'est nécessaire : le jeu de données est public et téléchargé directement.

---

## Utilisation

Toutes les commandes se lancent depuis la racine du projet.

**Lancer le projet complet** (téléchargement, bases de données, entraînement, puis tableau de bord) :

```bash
python main.py
```

**Lancer uniquement le tableau de bord**, une fois le pipeline exécuté au moins une fois :

```bash
python -m streamlit run dashboard/app.py
```

Le tableau de bord s'ouvre dans le navigateur, à l'adresse `http://localhost:8501`.

**Afficher la matrice de corrélation** :

```bash
python -m ML.exploration
```

Les erreurs du pipeline et du tableau de bord sont enregistrées dans le dossier `logs/`.

> Sous Windows, la commande `streamlit` seule peut ne pas être reconnue si le dossier des scripts Python n'est pas dans le PATH. `python -m streamlit` fonctionne dans tous les cas.

---

## Tests

Les tests vérifient la qualité des données à chaque étape du pipeline :

- **ETL relationnel** : codes postaux sur 5 caractères, unicité des clés primaires, validité des clés étrangères, aucune ligne perdue, conversion des dates.
- **ETL analytique** : dimension date continue et sans doublon, cohérence des week-ends, clés de dates présentes dans `Dim_Date`, délais d'expédition positifs, mesures sans valeur manquante.
- **Modèle** : 12 prévisions numériques pour une année, prise en charge d'une catégorie inconnue.

Ils sont exécutés automatiquement par `main.py` après chaque étape : le pipeline s'arrête si un test échoue. Pour les lancer séparément :

```bash
python -m pytest -v
```

## Modélisation des données

### Base relationnelle (Merise)

Le CSV d'origine est une table unique de 21 colonnes, où les informations sur les clients, les produits et les adresses se répètent sur chaque ligne. Il est découpé en 6 tables normalisées :

| Table | Contenu |
|---|---|
| `sous_categorie` | Sous-catégories de produits et leur catégorie |
| `produit` | Catalogue des produits |
| `client` | Clients et segment |
| `localisation` | Adresses de livraison |
| `commande` | Commandes (dates, mode d'expédition, client, adresse) |
| `ligne_commande` | Produits de chaque commande, avec montant, quantité, remise et profit |

Le MCD et le MLD ont été réalisés avec Looping (`docs/MCD_Superstore.loo`).

**Modèle conceptuel de données (MCD)**

![MCD](docs/MCD_superstore.png)

**Modèle logique de données (MLD)**

![MLD](docs/MLD_superstore.png)

### Base analytique (modèle en étoile)

Le modèle en étoile est optimisé pour l'analyse et le tableau de bord. La table de faits contient une ligne par ligne de commande.

![Modèle en étoile](docs/diagramme_en_etoile_base_analytique.png)

| Table | Rôle |
|---|---|
| `Fact_Sales` | Mesures : ventes, quantité, remise, profit, délai d'expédition |
| `Dim_Date` | Calendrier continu (année, trimestre, mois, semaine, jour) |
| `Dim_Customer` | Clients et segment |
| `Dim_Product` | Produit, sous-catégorie et catégorie |
| `Dim_Location` | Pays, état, ville, région, code postal |
| `Dim_Shipping` | Mode d'expédition |

Le détail de chaque colonne est disponible dans le [dictionnaire des données](docs/Dictionnaire_des_données.md).

---

## Modèle de prévision

- **Cible** : chiffre d'affaires mensuel par catégorie et par région.
- **Variables** : année, mois, catégorie de produit, région.
- **Découpage** : entraînement sur les trois premières années, test sur la dernière.
- **Modèles comparés** : régression linéaire et Random Forest (scikit-learn), avec encodage des variables catégorielles dans un pipeline.
- **Évaluation** : MAE (erreur moyenne en dollars) et MAPE (erreur moyenne en pourcentage).

Le meilleur modèle est sauvegardé dans `data/modeles/prediction_ventes.joblib`, et les scores de chaque entraînement dans `data/modeles/rapport_entrainement.json`. Il est utilisé dans l'onglet Prévision du tableau de bord. L'interprétation des résultats se trouve dans [`docs/problematique.md`](docs/problematique.md).

---

## Tableau de bord

### Onglets

| Onglet | Contenu |
|---|---|
| Vue KPI | Chiffre d'affaires, profit, marge et nombre de commandes ; évolution mensuelle du CA et du profit |
| Clients | Répartition des clients par segment, CA et profit par segment, top 10 des clients |
| Commerciale | CA par catégorie et par sous-catégorie, top 10 des produits |
| Géographique | Carte du chiffre d'affaires par état |
| Logistique | Nombre de commandes et délai moyen par mode d'expédition |
| Rentabilité | Profit et marge par catégorie, profit par sous-catégorie, impact des remises, produits les moins rentables |
| Temporelle | CA annuel et évolution, tendance mensuelle, saisonnalité |
| Prévision | Prévision du CA mensuel de l'année suivante, par catégorie et par région, comparée à l'historique |

### Filtres

Le panneau latéral permet de filtrer les données par **année** et par **région**. Les filtres s'appliquent à tous les onglets, sauf à l'onglet Prévision, qui dispose de ses propres sélecteurs de catégorie et de région et affiche toujours l'historique complet.

### Principaux enseignements

- **Saisonnalité** : le profil des ventes se répète chaque année. Janvier et février sont les mois les plus faibles, et les pics se situent en septembre, novembre et décembre, avec un creux récurrent en octobre.
- **Tendance** : 2011 et 2012 sont à des niveaux proches, puis le chiffre d'affaires progresse en 2013 et surtout en 2014, année la plus forte de juin à novembre.
- **Remises** : les ventes sans remise génèrent la grande majorité du profit, et les remises de 10 % à 20 % restent rentables. À partir de 30 % de remise, tous les niveaux sont déficitaires.
- **Clients** : [à compléter à partir de l'onglet Clients : quel segment apporte le plus de CA et de profit ?]
- **Produits** : [à compléter à partir des onglets Commerciale et Rentabilité : quelles sous-catégories vendent le plus, et lesquelles perdent de l'argent ?]
- **Géographie** : [à compléter à partir de l'onglet Géographique : quels états concentrent les ventes ?]
- **Logistique** : [à compléter à partir de l'onglet Logistique : mode d'expédition le plus utilisé et écart de délai entre les modes.]

---

## Technologies

| Domaine | Outils |
|---|---|
| Langage | Python |
| Données | pandas, NumPy |
| Base de données | DuckDB |
| Machine learning | scikit-learn, joblib |
| Visualisation | Plotly, Matplotlib, Seaborn |
| Tableau de bord | Streamlit |
| Modélisation | Looping (MCD/MLD) |

---

## Défis et badges

**Défis réalisés** : Star Schema, Merise (MCD/MLD), Streamlit, DuckDB, Random Forest, comparaison de plusieurs modèles, régression linéaire, matrice de corrélation.

| Badge | Réalisation |
|---|---|
| Data Engineer | ETL complet, bases alimentées automatiquement, DuckDB |
| Data Architect | MCD/MLD, dictionnaire des données, modèle en étoile |
| Data Analyst | KPI, visualisations, tableau de bord interactif avec filtres, analyse des résultats |
| IA | Préparation des données, entraînement et évaluation de modèles scikit-learn, prévision intégrée au tableau de bord |
| Développeur Data | Application Streamlit, code Python structuré |