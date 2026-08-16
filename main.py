import logging

from etl.extract import extract
from etl.transform import transform
from etl.load import load

logging.basicConfig(level=logging.INFO, format="(%asctime)s | %(message)s")

def main():
    extract()
    transform()
    load()

if __name__ == "__main__":
    main()