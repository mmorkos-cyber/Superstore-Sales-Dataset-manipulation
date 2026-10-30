# Problématique et résultats

## 1. Quelle est votre problématique ?

**Peut-on prévoir le chiffre d'affaires mensuel de Superstore, par catégorie de produit et par région, à partir de l'historique de ses ventes ?**

Le jeu de données Superstore Sales contient 9 994 lignes de commande d'une enseigne américaine de fournitures (mobilier, fournitures de bureau, matériel technologique), réparties sur quatre années. L'objectif est d'utiliser les trois premières années pour prévoir les ventes de la dernière, mois par mois, pour chaque combinaison catégorie × région.

## 2. Pourquoi est-elle intéressante ?

Prévoir les ventes est l'une des questions les plus courantes en entreprise, car beaucoup de décisions en dépendent :

- **Gestion des stocks** : commander assez pour ne pas manquer de produits pendant les mois forts, sans immobiliser de trésorerie dans des stocks inutiles pendant les mois creux.
- **Budget et objectifs commerciaux** : fixer des objectifs réalistes par région et par catégorie, et repérer rapidement un écart entre les ventes réelles et les ventes attendues.
- **Planification** : anticiper les besoins en personnel et en logistique lors des pics d'activité.

Prévoir par catégorie et par région, plutôt qu'un seul total, rend la prévision directement exploitable : un responsable régional ou un acheteur peut lire la prévision qui le concerne.

## 3. Quelles hypothèses formulez-vous ?

- **H1 — Saisonnalité** : les ventes suivent un cycle annuel, avec des mois plus forts que d'autres, en particulier en fin d'année.
- **H2 — Tendance** : le chiffre d'affaires évolue d'une année sur l'autre, ce qui permet d'utiliser l'année comme variable de prévision.
- **H3 — Catégorie et région** : le niveau des ventes dépend de la catégorie de produit et de la région, certaines catégories et régions vendant structurellement plus que d'autres.
- **H4 — Remises et rentabilité** : les remises importantes augmentent les volumes mais dégradent la rentabilité, au point de rendre certaines ventes déficitaires.

## 4. Vos résultats répondent-ils à la question ?

### Démarche

- **Données** : les ventes ont été agrégées par mois, catégorie et région, à partir de la base analytique (modèle en étoile).
- **Variables explicatives** : année, mois, catégorie de produit, région. Les variables connues uniquement après la vente (profit, quantité) ont été exclues, pour éviter que le modèle utilise la réponse pour trouver la réponse.
- **Découpage temporel** : entraînement sur les trois premières années, test sur la dernière, que le modèle n'a jamais vue. Un découpage aléatoire aurait permis au modèle d'apprendre sur des mois postérieurs à ceux qu'il prédit, ce qui ne correspond pas à une situation réelle de prévision.
- **Modèles comparés** : régression linéaire et Random Forest, évalués avec la MAE (erreur moyenne en dollars) et la MAPE (erreur moyenne en pourcentage).

### Résultats des modèles

| Modèle | MAE | MAPE |
|---|---|---|
| Régression linéaire | 2 372 $ | 118 % |
| Random Forest | 2 610 $ | 251 % |

**Modèle retenu : régression linéaire**, qui obtient la MAE la plus faible.

> Les valeurs exactes de chaque entraînement sont enregistrées dans `data/modeles/rapport_entrainement.json`.

### Interprétation

**Les prévisions donnent un ordre de grandeur, mais pas une prévision précise.** Une erreur moyenne d'environ 2 400 $ par mois et par groupe est élevée par rapport aux montants prédits, et une MAPE supérieure à 100 % signifie que l'erreur dépasse en moyenne la valeur réelle elle-même.

**La MAPE est gonflée par les petits mois.** Certaines combinaisons catégorie × région ont des ventes mensuelles faibles. Sur ces lignes, une erreur de quelques centaines de dollars représente plusieurs fois la valeur réelle, ce qui fait exploser la moyenne des pourcentages. La MAE est donc l'indicateur le plus fiable pour comparer les modèles ici.

**Pourquoi la régression linéaire fait mieux que le Random Forest.** Le Random Forest ne peut pas prédire au-delà des valeurs vues pendant l'entraînement : l'année de test n'existe pas dans les données d'entraînement, et les arbres la traitent comme la dernière année connue. Il ne peut donc pas prolonger une tendance. La régression linéaire, elle, attribue un coefficient à l'année et peut extrapoler une évolution. Le jeu d'entraînement est aussi petit (quelques centaines de lignes mensuelles), ce qui limite l'avantage d'un modèle plus complexe.

**Le modèle ne reproduit pas la saisonnalité.** La régression linéaire traite le mois comme un nombre : elle apprend un montant fixe ajouté chaque mois, et prévoit donc une ligne droite de janvier à décembre. Elle ne peut pas reproduire les pics de septembre, novembre et décembre ni le creux d'octobre, pourtant bien visibles dans les données (voir H1). Une partie importante de l'erreur vient de là.

### Vérification des hypothèses

- **H1 — Saisonnalité** : **confirmée.** Le graphique de saisonnalité montre un profil qui se répète chaque année. Les ventes sont au plus bas en janvier et février, remontent en mars, restent à un niveau intermédiaire d'avril à août, puis atteignent leurs pics en septembre, novembre et décembre. Octobre marque chaque année un creux entre les pics de septembre et de novembre. Le dernier trimestre et le mois de septembre concentrent donc une grande partie de l'activité.
- **H2 — Tendance** : **confirmée.** Les courbes de 2011 et 2012 sont à des niveaux proches, tandis que 2013 et surtout 2014 se situent au-dessus pour la plupart des mois : en 2014, le chiffre d'affaires est le plus élevé des quatre années de juin à novembre, avec un pic à plus de 110 000 $ en novembre.
- **H3 — Catégorie et région** : **partiellement confirmée.** La matrice de corrélation montre que la catégorie est la seule variable descriptive liée au montant d'une ligne de vente (Technology : +0,17, Office Supplies : −0,22). La région, le segment et le mode d'expédition ont une corrélation proche de 0 au niveau de la ligne de commande.
- **H4 — Remises et rentabilité** : **confirmée.** La corrélation entre remise et profit est négative (−0,22), et le graphique « Profit par niveau de remise » montre un seuil net : les ventes sans remise génèrent la grande majorité du profit (plus de 300 000 $), et les remises de 10 % à 20 % restent rentables. À partir de 30 % de remise, tous les niveaux sont déficitaires, avec les pertes les plus importantes à 70 % et 80 %. Les remises supérieures à 20 % font donc perdre de l'argent à l'entreprise.

À noter : les variables de date (mois, année) ont une corrélation proche de 0 avec les ventes au niveau de la ligne de commande. Cela ne contredit pas H1 et H2 : le montant d'une ligne varie énormément (de moins de 1 $ à plus de 22 000 $), ce qui masque les effets de calendrier. Ces effets n'apparaissent que sur les totaux mensuels, comme le montre le graphique de saisonnalité, d'où le choix d'entraîner le modèle sur des données agrégées par mois.

### Conclusion

**Les résultats répondent partiellement à la question.** Le modèle capte le niveau général des ventes selon la catégorie et la région, mais son erreur reste trop élevée pour une utilisation opérationnelle, comme le pilotage des stocks mois par mois.

Pistes d'amélioration :

- **Traiter le mois comme une catégorie** plutôt que comme un nombre, en l'ajoutant aux variables encodées par le `OneHotEncoder`, pour que le modèle apprenne une valeur propre à chaque mois et puisse capter la saisonnalité.
- **Ajouter les ventes des mois précédents** comme variables (ventes du mois précédent, du même mois l'année précédente), qui sont généralement les meilleurs indicateurs pour prévoir des ventes.
- **Prévoir à un niveau plus agrégé** (par catégorie seulement, ou au total), où les ventes mensuelles sont moins bruitées.
- **Disposer de plus d'historique** : quatre années donnent peu de cycles saisonniers pour apprendre la saisonnalité.