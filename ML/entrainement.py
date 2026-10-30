from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.base import clone
from sklearn.metrics import (mean_absolute_error, mean_absolute_percentage_error)
from ML.exploration import charger_donnees_analytiques
import json
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

FICHIER_MODELES = BASE_DIR / "data" / "modeles" / "prediction_ventes.joblib"
FICHIER_RAPPORT = FICHIER_MODELES.parent / "rapport_entrainement.json"

preparation = ColumnTransformer([("categories", OneHotEncoder(handle_unknown="ignore"), ["product_category", "region"])], remainder="passthrough")

modeles = {
    "Random Forest": RandomForestRegressor( n_estimators=20, max_depth=10, random_state=42, n_jobs=-1),
    "Régression linéaire": LinearRegression()
}


def main():
    df = charger_donnees_analytiques()

    df_mensuel = (df.groupby(["annee", "mois", "product_category", "region"])["sales"].sum().reset_index())

    X = df_mensuel[["annee", "mois", "product_category", "region"]]
    y = df_mensuel["sales"]

    derniere_annee = df_mensuel["annee"].max()

    X_train = X[df_mensuel["annee"] < derniere_annee]
    y_train = y[df_mensuel["annee"] < derniere_annee]
    X_test = X[df_mensuel["annee"] == derniere_annee]
    y_test = y[df_mensuel["annee"] == derniere_annee]

    resultats = {}

    for nom, modele in modeles.items():
        pipeline = Pipeline([("preparation", clone(preparation)), ("modele", modele)])
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)

        mae = mean_absolute_error(y_test, predictions)
        mape = mean_absolute_percentage_error(y_test, predictions)
        resultats[nom] = {"pipeline": pipeline, "mae": mae, "mape": mape}

        print(f"{nom} : MAE = {mae:.2f} $, MAPE = {mape:.1%}")

    meilleur_nom = min(resultats, key=lambda nom: resultats[nom]["mae"])

    FICHIER_MODELES.parent.mkdir(parents=True, exist_ok=True)

    rapport = {
        "date_entrainement": datetime.now().isoformat(timespec="seconds"),
        "annee_test": int(derniere_annee),
        "nb_lignes_entrainement": len(X_train),
        "nb_lignes_test": len(X_test),
        "modeles": {nom: {"mae": round(res["mae"], 2), "mape": round(res["mape"], 4)} for nom, res in resultats.items()},
        "modele_retenu": meilleur_nom,
    }

    FICHIER_RAPPORT.write_text(json.dumps(rapport, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Rapport : {FICHIER_RAPPORT}")

    joblib.dump(resultats[meilleur_nom]["pipeline"], FICHIER_MODELES)

    print(f"Modèle sauvegardé : {meilleur_nom}")


if __name__ == "__main__":
    main()