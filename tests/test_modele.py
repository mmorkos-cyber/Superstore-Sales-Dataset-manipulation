from pathlib import Path

import joblib
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
FICHIER_MODELE = BASE_DIR / "data" / "modeles" / "prediction_ventes.joblib"

pytestmark = pytest.mark.skipif(not FICHIER_MODELE.exists(), reason="Modèle absent : lancer d'abord python main.py")


@pytest.fixture
def modele():
    return joblib.load(FICHIER_MODELE)


@pytest.fixture
def donnees_une_annee():
    return pd.DataFrame({
        "annee": [2015] * 12,
        "mois": list(range(1, 13)),
        "product_category": ["Furniture"] * 12,
        "region": ["West"] * 12,
    })


def test_douze_predictions(modele, donnees_une_annee):
    predictions = modele.predict(donnees_une_annee)

    assert len(predictions) == 12


def test_predictions_sont_des_nombres(modele, donnees_une_annee):
    predictions = pd.Series(modele.predict(donnees_une_annee))

    assert predictions.notna().all()
    assert pd.api.types.is_numeric_dtype(predictions)


def test_categorie_inconnue_acceptee(modele):
    donnees = pd.DataFrame({
        "annee": [2015],
        "mois": [1],
        "product_category": ["Catégorie inconnue"],
        "region": ["West"],
    })

    predictions = modele.predict(donnees)

    assert len(predictions) == 1