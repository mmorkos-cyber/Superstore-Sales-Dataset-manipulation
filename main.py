import duckdb
from utils import dl_fichier_raw
from ETL_relationnelle import load
from ETL_analytique import load_analytique
from ML import entrainement

def main():
    
    print("=== Étape 1 : téléchargement et extraction ===")
    dl_fichier_raw.run()

    try:
        load.run_ETL()
    except duckdb.ConstraintException:
        print("Base relationnelle déjà remplie, étape ignorée.")

    print("=== Étape 3 : construction de la base analytique ===")
    load_analytique.run_analytique()

    print("=== Étape 4 : entrainement du modele ===")
    entrainement.main()


if __name__ == "__main__":
    main()