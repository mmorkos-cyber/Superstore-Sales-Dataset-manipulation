import duckdb
from pathlib import Path
from ETL_relationnelle.transform import (prepa_df_client, prepa_df_localisation, prepa_df_produit, prepa_df_category, prepa_df_sous_category, prepa_df_commande, prepa_df_ligne_commande)
from utils.logger import get_logger

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data" / "db"
FICHIER_DB = DB_DIR / "Superstore_relationnelle.db"

lg = get_logger("etl_relationnelle", "ETL_error_relationnelle.log")

DB_DIR.mkdir(parents=True, exist_ok=True)
conn = duckdb.connect(str(FICHIER_DB))


def init_db():
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categorie (
            categorie TEXT PRIMARY KEY
        );

        CREATE TABLE IF NOT EXISTS sous_categorie (
            sous_categorie TEXT PRIMARY KEY,
            categorie TEXT NOT NULL REFERENCES categorie(categorie)
        );

        CREATE TABLE IF NOT EXISTS produit (
            produit_id TEXT PRIMARY KEY,
            nom TEXT NOT NULL,
            sous_categorie TEXT NOT NULL REFERENCES sous_categorie(sous_categorie)
        );

        CREATE TABLE IF NOT EXISTS client (
            client_id TEXT PRIMARY KEY,
            nom TEXT NOT NULL,
            segment TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS localisation (
            localisation_id INTEGER PRIMARY KEY,
            pays TEXT NOT NULL,
            etat TEXT NOT NULL,
            ville TEXT NOT NULL,
            region TEXT NOT NULL,
            code_postal TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS commande (
            commande_id TEXT PRIMARY KEY,
            date_commande DATE NOT NULL,
            date_expedition DATE NOT NULL,
            mode_expedition TEXT NOT NULL,
            client_id TEXT NOT NULL REFERENCES client(client_id),
            localisation_id INTEGER NOT NULL REFERENCES localisation(localisation_id)
        );

        CREATE TABLE IF NOT EXISTS ligne_commande (
            ligne_id INTEGER PRIMARY KEY,
            commande_id TEXT NOT NULL REFERENCES commande(commande_id),
            produit_id TEXT NOT NULL REFERENCES produit(produit_id),
            ventes DOUBLE NOT NULL,
            quantite INTEGER NOT NULL,
            remise DOUBLE NOT NULL,
            profit DOUBLE NOT NULL
        );
    """)


def inserer_donnees():
    tables = [("categorie", prepa_df_category()), ("sous_categorie", prepa_df_sous_category()), ("produit", prepa_df_produit()), ("client", prepa_df_client()), ("localisation", prepa_df_localisation()), ("commande", prepa_df_commande()), ("ligne_commande", prepa_df_ligne_commande()),]

    for nom_table, df_table in tables:
        try:
            conn.register("df_temp", df_table)
            conn.execute(f"INSERT INTO {nom_table} BY NAME SELECT * FROM df_temp")
            conn.unregister("df_temp")
            print(f"{nom_table} : {len(df_table)} lignes insérées")
        except Exception as e:
            lg.error(f"Erreur d'insertion dans {nom_table} : {e}")
            raise

def run_ETL():
    init_db()
    inserer_donnees()

if __name__ == "__main__":
    try:
        run_ETL()
    except Exception as e:
        lg.error(f"Erreur Pendant le chargement de la base relaionelle : {e}")
        raise
    finally:
        conn.close()