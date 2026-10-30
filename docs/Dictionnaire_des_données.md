# Dictionnaire des données

Ce document décrit l'ensemble des tables et colonnes du projet Superstore Sales.

- **Source** : fichier `Superstore.csv` (Kaggle — Superstore Sales), 9 994 lignes, 21 colonnes, encodage Windows-1252.
- **Base relationnelle** : `data/db/Superstore_relationnelle.db` (DuckDB), modèle normalisé issu du MCD/MLD (Merise).
- **Base analytique** : `data/db/Superstore_analytique.db` (DuckDB), modèle en étoile (Star Schema) construit à partir de la base relationnelle.

**Légende des contraintes** : PK = clé primaire, FK = clé étrangère, NN = NOT NULL, UQ = UNIQUE.

---

## 1. Base relationnelle

### Table `sous_categorie`

Sous-catégories de produits, rattachées à une catégorie.

| Colonne | Type | Contraintes | Description | Exemple | Colonne source |
|---|---|---|---|---|---|
| `sous_categorie` | TEXT | PK | Nom de la sous-catégorie | `Bookcases` | Sub-Category |
| `categorie` | TEXT |  NN | Catégorie à laquelle appartient la sous-catégorie | `Furniture` | Category |

### Table `produit`

Catalogue des produits vendus.

| Colonne | Type | Contraintes | Description | Exemple | Colonne source |
|---|---|---|---|---|---|
| `produit_id` | TEXT | PK | Identifiant unique du produit | `FUR-BO-10001798` | Product ID |
| `nom` | TEXT | NN | Nom commercial du produit | `Bush Somerset Collection Bookcase` | Product Name |
| `sous_categorie` | TEXT | FK → `sous_categorie(sous_categorie)`, NN | Sous-catégorie du produit | `Bookcases` | Sub-Category |

### Table `client`

Clients ayant passé au moins une commande.

| Colonne | Type | Contraintes | Description | Exemple | Colonne source |
|---|---|---|---|---|---|
| `client_id` | TEXT | PK | Identifiant unique du client | `CG-12520` | Customer ID |
| `nom` | TEXT | NN | Nom complet du client | `Claire Gute` | Customer Name |
| `segment` | TEXT | NN | Segment de clientèle (`Consumer`, `Corporate`, `Home Office`) | `Consumer` | Segment |

### Table `localisation`

Adresses de livraison (une ligne par combinaison unique pays / état / ville / région / code postal).

| Colonne | Type | Contraintes | Description | Exemple | Colonne source |
|---|---|---|---|---|---|
| `localisation_id` | INTEGER | PK | Identifiant de la localisation, généré lors de l'ETL | `1` | — (calculé) |
| `pays` | TEXT | NN | Pays de livraison | `United States` | Country |
| `etat` | TEXT | NN | État américain de livraison | `Kentucky` | State |
| `ville` | TEXT | NN | Ville de livraison | `Henderson` | City |
| `region` | TEXT | NN | Région commerciale (`Central`, `East`, `South`, `West`) | `South` | Region |
| `code_postal` | TEXT | NN | Code postal sur 5 caractères (zéros initiaux conservés) | `01040` | Postal Code |

### Table `commande`

Commandes passées par les clients (une ligne par commande).

| Colonne | Type | Contraintes | Description | Exemple | Colonne source |
|---|---|---|---|---|---|
| `commande_id` | TEXT | PK | Identifiant unique de la commande | `CA-2011-100006` | Order ID |
| `date_commande` | DATE | NN | Date de passage de la commande | `2011-09-07` | Order Date |
| `date_expedition` | DATE | NN | Date d'expédition de la commande | `2011-09-13` | Ship Date |
| `mode_expedition` | TEXT | NN | Mode de livraison (`Standard Class`, `Second Class`, `First Class`, `Same Day`) | `Second Class` | Ship Mode |
| `client_id` | TEXT | FK → `client(client_id)`, NN | Client ayant passé la commande | `CG-12520` | Customer ID |
| `localisation_id` | INTEGER | FK → `localisation(localisation_id)`, NN | Adresse de livraison de la commande | `1` | — (calculé) |

### Table `ligne_commande`

Lignes de commande : un produit dans une commande.

| Colonne | Type | Contraintes | Description | Exemple | Colonne source |
|---|---|---|---|---|---|
| `ligne_id` | INTEGER | PK | Identifiant unique de la ligne | `1` | Row ID |
| `commande_id` | TEXT | FK → `commande(commande_id)`, NN | Commande à laquelle appartient la ligne | `CA-2013-152156` | Order ID |
| `produit_id` | TEXT | FK → `produit(produit_id)`, NN | Produit commandé | `FUR-BO-10001798` | Product ID |
| `ventes` | DOUBLE | NN | Montant de la ligne en dollars, remise appliquée | `261.96` | Sales |
| `quantite` | INTEGER | NN | Nombre d'unités commandées | `2` | Quantity |
| `remise` | DOUBLE | NN | Taux de remise appliqué, entre 0 et 1 (0.2 = 20 %) | `0.0` | Discount |
| `profit` | DOUBLE | NN | Profit de la ligne en dollars (négatif en cas de perte) | `41.91` | Profit |

---

## 2. Base analytique (Star Schema)

### Table de dimension `Dim_Date`

Calendrier continu couvrant toute la période, de la première date de commande à la dernière date d'expédition (y compris les jours sans vente).

| Colonne | Type | Contraintes | Description | Exemple | Origine |
|---|---|---|---|---|---|
| `date_id` | INTEGER | PK | Clé de la date au format AAAAMMJJ | `20131109` | Calculé |
| `date_complete` | DATE | NN | Date du jour | `2013-11-09` | Calculé (`pd.date_range`) |
| `annee` | INTEGER | NN | Année | `2013` | Calculé |
| `trimestre` | INTEGER | NN | Trimestre (1 à 4) | `4` | Calculé |
| `mois` | INTEGER | NN | Numéro du mois (1 à 12) | `11` | Calculé |
| `nom_mois` | TEXT | NN | Nom du mois en français | `Novembre` | Calculé |
| `semaine` | INTEGER | NN | Numéro de semaine ISO | `45` | Calculé |
| `jour_semaine` | TEXT | NN | Nom du jour en français | `Samedi` | Calculé |
| `est_weekend` | BOOLEAN | NN | Vrai si samedi ou dimanche | `true` | Calculé |

### Table de dimension `Dim_Customer`

| Colonne | Type | Contraintes | Description | Exemple | Origine |
|---|---|---|---|---|---|
| `customer_id` | TEXT | PK | Identifiant unique du client | `CG-12520` | `client.client_id` |
| `customer_name` | TEXT | NN | Nom complet du client | `Claire Gute` | `client.nom` |
| `segment` | TEXT | NN | Segment de clientèle | `Consumer` | `client.segment` |

### Table de dimension `Dim_Product`

Dimension dénormalisée : regroupe produit, sous-catégorie et catégorie.

| Colonne | Type | Contraintes | Description | Exemple | Origine |
|---|---|---|---|---|---|
| `product_id` | TEXT | PK | Identifiant unique du produit | `FUR-BO-10001798` | `produit.produit_id` |
| `product_name` | TEXT | NN | Nom commercial du produit | `Bush Somerset Collection Bookcase` | `produit.nom` |
| `product_category` | TEXT | NN | Catégorie du produit | `Furniture` | `sous_categorie.categorie` |
| `product_sub_category` | TEXT | NN | Sous-catégorie du produit | `Bookcases` | `produit.sous_categorie` |

### Table de dimension `Dim_Location`

| Colonne | Type | Contraintes | Description | Exemple | Origine |
|---|---|---|---|---|---|
| `id_dim_location` | INTEGER | PK | Identifiant de la localisation | `1` | `localisation.localisation_id` |
| `country` | TEXT | NN | Pays de livraison | `United States` | `localisation.pays` |
| `state` | TEXT | NN | État américain de livraison | `Kentucky` | `localisation.etat` |
| `city` | TEXT | NN | Ville de livraison | `Henderson` | `localisation.ville` |
| `region` | TEXT | NN | Région commerciale | `South` | `localisation.region` |
| `postal_code` | TEXT | NN | Code postal sur 5 caractères | `01040` | `localisation.code_postal` |

### Table de dimension `Dim_Shipping`

| Colonne | Type | Contraintes | Description | Exemple | Origine |
|---|---|---|---|---|---|
| `id_dim_shipping` | INTEGER | PK | Identifiant du mode d'expédition, généré lors de l'ETL | `2` | Calculé |
| `shipping_mode` | TEXT | NN, UQ | Mode de livraison | `Second Class` | `commande.mode_expedition` |

### Table de faits `Fact_Sales`

Grain : une ligne par ligne de commande (un produit dans une commande).

| Colonne | Type | Contraintes | Description | Exemple | Origine |
|---|---|---|---|---|---|
| `id_fact_sales` | INTEGER | PK | Identifiant de la ligne de vente | `1` | `ligne_commande.ligne_id` |
| `order_id` | TEXT | NN | Identifiant de la commande (dimension dégénérée) | `CA-2013-152156` | `ligne_commande.commande_id` |
| `id_date_commande` | INTEGER | FK → `Dim_Date(date_id)`, NN | Date de commande | `20131109` | Calculé depuis `commande.date_commande` |
| `id_date_expedition` | INTEGER | FK → `Dim_Date(date_id)`, NN | Date d'expédition | `20131112` | Calculé depuis `commande.date_expedition` |
| `customer_id` | TEXT | FK → `Dim_Customer(customer_id)`, NN | Client | `CG-12520` | `commande.client_id` |
| `product_id` | TEXT | FK → `Dim_Product(product_id)`, NN | Produit | `FUR-BO-10001798` | `ligne_commande.produit_id` |
| `id_dim_location` | INTEGER | FK → `Dim_Location(id_dim_location)`, NN | Adresse de livraison | `1` | `commande.localisation_id` |
| `id_dim_shipping` | INTEGER | FK → `Dim_Shipping(id_dim_shipping)`, NN | Mode d'expédition | `2` | Calculé depuis `commande.mode_expedition` |
| `sales` | DOUBLE | NN | Montant de la ligne en dollars, remise appliquée | `261.96` | `ligne_commande.ventes` |
| `quantity` | INTEGER | NN | Nombre d'unités commandées | `2` | `ligne_commande.quantite` |
| `discount` | DOUBLE | NN | Taux de remise, entre 0 et 1 | `0.0` | `ligne_commande.remise` |
| `profit` | DOUBLE | NN | Profit de la ligne en dollars | `41.91` | `ligne_commande.profit` |
| `shipping_delay` | INTEGER | NN | Délai d'expédition en jours (date d'expédition − date de commande) | `3` | Calculé |

---

## 3. Règles de transformation appliquées

| Règle | Colonnes concernées | Détail |
|---|---|---|
| Encodage | Fichier source | Lecture en Windows-1252 (`cp1252`) : le fichier contient des espaces insécables (`0xA0`) non valides en UTF-8 |
| Conversion des dates | Order Date, Ship Date | Texte au format `JJ-MM-AAAA` converti en type DATE |
| Codes postaux | Postal Code | Convertis en texte et complétés à 5 caractères (`1040` → `01040`) |
| Dédoublonnage | Toutes les tables de référence | Une ligne par valeur de clé primaire |
| Clés générées | `localisation_id`, `id_dim_shipping`, `date_id` | Générées pendant l'ETL, absentes du fichier source |
| Délai d'expédition | `shipping_delay` | Différence en jours entre la date d'expédition et la date de commande |