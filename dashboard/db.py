
import duckdb
import streamlit as st

from pathlib import Path
import duckdb

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data" / "db"
FICHIER_DB = DB_DIR / "Superstore_analytique.db"



from utils.logger import get_logger
lg = get_logger("analyse", "analyse_error.log")


@st.cache_resource
def get_connection():
    try:
        return duckdb.connect(FICHIER_DB)
    except Exception as e:
        lg.error(f"Erreur de chargement de la BDD {e}")

