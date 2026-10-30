import duckdb
import subprocess
import sys
from utils import dl_fichier_raw
import pytest

def lancer_tests(fichier):
    resultat = pytest.main(["-v", fichier])
    return resultat == 0


def main():

    print("=== Étape 1 : téléchargement et extraction ===")
    dl_fichier_raw.run()

    print("=== Étape 2 : construction de la base relationnelle ===")
    from ETL_relationnelle import load
    try:
        load.run_ETL()
    except duckdb.ConstraintException:
        print("Base relationnelle déjà remplie, étape ignorée.")
    load.conn.close()

    if not lancer_tests("tests/test_etl_relationnelle.py"):
        print("Tests de l'ETL relationnel échoués : arrêt du pipeline.")
        return

    print("=== Étape 3 : construction de la base analytique ===")
    from ETL_analytique import load_analytique
    load_analytique.run_analytique()
    load_analytique.conn.close()

    if not lancer_tests("tests/test_etl_analytique.py"):
        print("Tests de l'ETL analytique échoués : arrêt du pipeline.")
        return

    print("=== Étape 4 : entrainement du modele ===")
    from ML import entrainement
    entrainement.main()

    if not lancer_tests("tests/test_modele.py"):
        print("Tests du modèle échoués : arrêt du pipeline.")
        return

    print("=== Étape 5 : lancer le dashboard ===")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard/app.py"])

if __name__ == "__main__":
    main()