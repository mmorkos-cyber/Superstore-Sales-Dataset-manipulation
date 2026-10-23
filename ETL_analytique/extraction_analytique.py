import pandas as pd
from pathlib import Path
import duckdb

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data" / "db"
FICHIER_DB = DB_DIR / "Superstore_relationnelle.db"
from utils.logger import get_logger

lg = get_logger("etl_analytique", "ETL_analytique_error.log")

DB_DIR.mkdir(parents=True, exist_ok=True)
conn = duckdb.connect(str(FICHIER_DB))


dataframe = []
df = None
try:
    df_dim_client = conn.execute("""SELECT client_id, nom AS nom_client, segment FROM client""").df()

    df_dim_geographie = conn.execute("""SELECT localisation_id AS geographie_id, pays, region, etat, ville, code_postal FROM localisation""").df()

    df_dim_produit = conn.execute("""SELECT p.produit_id, p.nom AS nom_produit, p.sous_categorie, sc.categorie FROM produit p JOIN sous_categorie sc ON p.sous_categorie = sc.sous_categorie""").df()

    df_modes = conn.execute("""SELECT DISTINCT mode_expedition FROM commande ORDER BY mode_expedition""").df()

    df_faits = conn.execute("""SELECT lc.ligne_id, lc.commande_id, c.date_commande, c.date_expedition, lc.produit_id, c.client_id, c.localisation_id AS geographie_id, c.mode_expedition, lc.ventes, lc.quantite, lc.remise, lc.profit FROM ligne_commande lc JOIN commande c ON lc.commande_id = c.commande_id""").df()
except Exception as e:
    lg.error(f"Erreur de lecture base relationnelle : {e}")
    raise
