import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data" / "db"
FICHIER_DB = DB_DIR / "Superstore_analytique.db"

print("Base DuckDB :", FICHIER_DB)



def charger_donnees_analytiques(limit=None):
    connexion = duckdb.connect(str(FICHIER_DB))
    requete = """
            SELECT f.sales, f.quantity, f.discount, f.profit, f.shipping_delay, d.annee, d.trimestre, d.mois, d.semaine, d.jour_semaine, d.est_weekend, p.product_category, c.segment, l.region, s.shipping_mode
            FROM Fact_Sales f
            LEFT JOIN Dim_Date d ON f.id_date_commande = d.date_id
            LEFT JOIN Dim_Product p ON f.product_id = p.product_id
            LEFT JOIN Dim_Customer c ON f.customer_id = c.customer_id
            LEFT JOIN Dim_Location l ON f.id_dim_location = l.id_dim_location
            LEFT JOIN Dim_Shipping s ON f.id_dim_shipping = s.id_dim_shipping
            """
    if limit is not None:
        requete += f" LIMIT {limit}"

    df = connexion.execute(requete).df()
    connexion.close()
    return df


def preparer_dataframe_ml(df):
    df_ml = df.copy()
    colonnes_ml = ["sales", "quantity", "discount", "profit", "shipping_delay", "annee", "trimestre", "mois", "semaine", "jour_semaine", "est_weekend", "product_category", "segment", "region", "shipping_mode"]
    df_ml = df_ml[colonnes_ml]
    df_ml = df_ml.dropna()
    return df_ml


if __name__ == "__main__":
    df = charger_donnees_analytiques()

    df_ml = preparer_dataframe_ml(df)

    # Encodage des variables catégorielles
    df_correlation = pd.get_dummies(df_ml, columns=["jour_semaine","product_category","segment","region","shipping_mode"], drop_first=False)

    correlation = df_correlation.corr(numeric_only=True)

    print("Matrice de corrélation :")
    print(correlation)

    correlation_ventes = (correlation["sales"].sort_values(ascending=False))

    print("\nCorrélation avec sales :")
    print(correlation_ventes)

    plt.figure(figsize=(16, 12))

    sns.heatmap(correlation, annot=True, fmt=".2f", cmap="coolwarm", center=0, annot_kws={"size": 7})

    plt.title("Matrice de corrélation des variables")
    plt.tight_layout()
    plt.show()

# # ---------------------------------
# # DEFINIR lA CIBLE Y
# # ---------------------------------

# y = df_ml["sales"]