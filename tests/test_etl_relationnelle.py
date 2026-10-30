from pathlib import Path

import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
FICHIER_CSV = BASE_DIR / "data" / "raw" / "Superstore.csv"

pytestmark = pytest.mark.skipif(not FICHIER_CSV.exists(), reason="CSV absent : lancer d'abord python main.py")


def test_codes_postaux_sur_5_caracteres():
    from ETL_relationnelle.transform import prepa_df_localisation

    df_localisation = prepa_df_localisation()

    assert df_localisation["code_postal"].str.len().eq(5).all()


def test_cles_primaires_uniques():
    from ETL_relationnelle.transform import (prepa_df_client, prepa_df_localisation, prepa_df_produit, prepa_df_sous_category, prepa_df_commande, prepa_df_ligne_commande)

    tables = [
        (prepa_df_client(), "client_id"),
        (prepa_df_localisation(), "localisation_id"),
        (prepa_df_produit(), "produit_id"),
        (prepa_df_sous_category(), "sous_categorie"),
        (prepa_df_commande(), "commande_id"),
        (prepa_df_ligne_commande(), "ligne_id"),
    ]

    for df_table, cle in tables:
        assert df_table[cle].is_unique, f"Doublons dans la clé {cle}"


def test_cles_etrangeres_existent():
    from ETL_relationnelle.transform import prepa_df_client, prepa_df_produit, prepa_df_commande, prepa_df_ligne_commande

    clients = prepa_df_client()
    produits = prepa_df_produit()
    commandes = prepa_df_commande()
    lignes = prepa_df_ligne_commande()

    assert commandes["client_id"].isin(clients["client_id"]).all()
    assert lignes["commande_id"].isin(commandes["commande_id"]).all()
    assert lignes["produit_id"].isin(produits["produit_id"]).all()


def test_aucune_ligne_perdue():
    from ETL_relationnelle.extraction import df
    from ETL_relationnelle.transform import prepa_df_ligne_commande

    assert len(prepa_df_ligne_commande()) == len(df)


def test_dates_converties():
    from ETL_relationnelle.transform import prepa_df_commande

    commandes = prepa_df_commande()

    assert pd.api.types.is_datetime64_any_dtype(commandes["date_commande"])
    assert pd.api.types.is_datetime64_any_dtype(commandes["date_expedition"])
    assert (commandes["date_expedition"] >= commandes["date_commande"]).all()