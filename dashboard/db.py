import duckdb
import streamlit as st
from pathlib import Path

from utils.logger import get_logger

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data" / "db"
FICHIER_DB = DB_DIR / "Superstore_analytique.db"

lg = get_logger("analyse", "analyse_error.log")


def get_connection():
    try:
        return duckdb.connect(str(FICHIER_DB), read_only=True)
    except Exception as e:
        lg.error(f"Erreur de chargement de la BDD {e}")