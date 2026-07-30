import logging as lg
import os

dossier_root =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dossier_logs = os.path.join(dossier_root, "logs")

os.makedirs(dossier_logs, exist_ok=True)

def get_logger(name, filename):

    logger = lg.getLogger(name)

    if not logger.handlers:

        logger.setLevel(lg.ERROR)

        file_handler = lg.FileHandler(os.path.join(dossier_logs, filename))

        formatter = lg.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    return logger