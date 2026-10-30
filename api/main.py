from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
FICHIER_MODELE = BASE_DIR / "data" / "modeles" / "prediction_ventes.joblib"

NOMS_MOIS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

app = FastAPI(
    title="API Prévision Superstore",
    description="Prévision du chiffre d'affaires mensuel de Superstore par catégorie de produit et par région.",
    version="1.0.0",
)

# Chargement du modèle une seule fois, au démarrage de l'API
try:
    modele = joblib.load(FICHIER_MODELE)
except FileNotFoundError:
    modele = None


class DemandePrevision(BaseModel):
    categorie: Literal["Furniture", "Office Supplies", "Technology"]
    region: Literal["Central", "East", "South", "West"]
    annee: int = Field(ge=2011, le=2100)


@app.get("/health")
def health():
    return {"status": "ok", "modele_charge": modele is not None}


@app.post("/prevision")
def prevision(demande: DemandePrevision):
    if modele is None:
        raise HTTPException(status_code=503, detail="Modèle indisponible : lancer d'abord l'entraînement (python main.py)")

    X = pd.DataFrame({
        "annee": [demande.annee] * 12,
        "mois": list(range(1, 13)),
        "product_category": [demande.categorie] * 12,
        "region": [demande.region] * 12,
    })

    ventes = modele.predict(X).clip(min=0)

    return {
        "categorie": demande.categorie,
        "region": demande.region,
        "annee": demande.annee,
        "total": round(float(ventes.sum()), 2),
        "mois": [{"mois": NOMS_MOIS[i], "ventes": round(float(v), 2)} for i, v in enumerate(ventes)],
    }