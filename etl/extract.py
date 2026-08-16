import logging 
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi
from dotenv import load_dotenv

load_dotenv()

DATASET = 'danilosoares/arena-corinthians'
OUTPUT_DIR = Path("data/raw")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

logger = logging.getLogger(__name__)

def extract():
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        logger.info("Iniciando extração do dataset '%s'...", DATASET)

        api = KaggleApi()
        api.authenticate()

        logger.info("Autenticação no Kaggle realizada com sucesso.")

        logger.info("Baixando dataset '%s'...", DATASET)

        api.dataset_download_files(
            DATASET, 
            path=OUTPUT_DIR, 
            unzip=True
        )

        logger.info("Arquivos salvos em '%s'.", OUTPUT_DIR)

    except Exception as e:
        logger.error(
            "Erro durante a extração do dataset '%s': %s",
            DATASET,
            e
        )
        raise