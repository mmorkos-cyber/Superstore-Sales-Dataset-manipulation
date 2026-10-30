from pathlib import Path

import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
FICHIER_DB_RELATIONNELLE = BASE_DIR / "data" / "db" / "Superstore_relationnelle.db"

# L'ETL analytique lit la base relationnelle dès son import :
# sans cette base, tous les tests de ce fichier sont ignorés.
pytestmark = pytest.mark.skipif(not FICHIER_DB_RELATIONNELLE.exists(), reason="Base relationnelle absente : lancer d'abord python main.py")


def test_dim_date_continue():
    from ETL_analytique.transform_analytique import dim_date_prep

    df_date = dim_date_prep()
    nb_jours_attendus = (df_date["date"].max() - df_date["date"].min()).days + 1

    assert len(df_date) == nb_jours_attendus
    assert df_date["date"].diff().dropna().dt.days.eq(1).all()


def test_dim_date_cle_unique():
    from ETL_analytique.transform_analytique import dim_date_prep

    df_date = dim_date_prep()

    assert df_date["date_id"].is_unique


def test_dim_date_weekend():
    from ETL_analytique.transform_analytique import dim_date_prep

    df_date = dim_date_prep()
    weekend = df_date[df_date["est_weekend"]]

    assert weekend["jour_semaine"].isin(["Samedi", "Dimanche"]).all()


def test_faits_dates_dans_dim_date():
    from ETL_analytique.transform_analytique import dim_date_prep, faits_ventes_prep

    df_date = dim_date_prep()
    df_ventes = faits_ventes_prep()

    assert df_ventes["date_commande_id"].isin(df_date["date_id"]).all()
    assert df_ventes["date_expedition_id"].isin(df_date["date_id"]).all()


def test_delai_expedition_positif():
    from ETL_analytique.transform_analytique import faits_ventes_prep

    df_ventes = faits_ventes_prep()

    assert (df_ventes["delai_expedition"] >= 0).all()


def test_mesures_sans_valeur_manquante():
    from ETL_analytique.transform_analytique import faits_ventes_prep

    df_ventes = faits_ventes_prep()
    mesures = ["ventes", "quantite", "remise", "profit"]

    assert not df_ventes[mesures].isna().any().any()
    assert pd.api.types.is_numeric_dtype(df_ventes["ventes"])