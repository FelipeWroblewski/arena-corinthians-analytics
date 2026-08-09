import logging
from pathlib import Path

import pandas as pd
import psycopg2.extras

from db.connection import connect_db

PROCESSED_DIR = Path("data/processed")
SQL_DIR = Path("sql")

logger = logging.getLogger(__name__)

TABLES = ["dim_jogos", "dim_jogadores", "fato_gols", "fato_escalacoes"]


def _run_sql_file(conn, path: Path):
    logger.info("Executando '%s'...", path)
    sql = path.read_text(encoding="utf-8")
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    except psycopg2.Error:
        conn.rollback()
        logger.error("Falha ao executar '%s'.", path)
        raise


def create_schema(conn):
    _run_sql_file(conn, SQL_DIR / "schema.sql")


def _insert_dataframe(conn, df: pd.DataFrame, tabela: str):
    if df.empty:
        logger.warning("DataFrame de '%s' está vazio; nada para inserir.", tabela)
        return

    columns = list(df.columns)
    columns_sql = ", ".join(f'"{c}"' for c in columns)

    df_clear = df.astype(object).where(pd.notnull(df), None)
    values = df_clear.values.tolist()

    query = f'INSERT INTO {tabela} ({columns_sql}) VALUES %s'

    try:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(cur, query, values)
        conn.commit()
    except psycopg2.Error:
        conn.rollback()
        logger.error("Falha ao inserir dados na tabela '%s'.", tabela)
        raise


def load_tables(conn):
    for name in TABLES:
        origin = PROCESSED_DIR / f"{name}.csv"
        try:
            df = pd.read_csv(origin)
        except FileNotFoundError:
            logger.error("Arquivo não encontrado: '%s'.", origin)
            raise
        _insert_dataframe(conn, df, name)
        logger.info("Carregado '%s' (%d linhas) na tabela '%s'.", origin, len(df), name)


def apply_views(conn):
    views_path = SQL_DIR / "views.sql"
    if not views_path.exists():
        logger.warning("Arquivo '%s' não encontrado; nenhuma view aplicada.", views_path)
        return

    _run_sql_file(conn, views_path)


def load():
    conn = connect_db()
    try:
        create_schema(conn)
        load_tables(conn)
        apply_views(conn)
    finally:
        conn.close()