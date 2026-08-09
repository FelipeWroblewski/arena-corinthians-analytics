import logging
import re
import unicodedata
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def _slugify_column(col: str) -> str:

    col = unicodedata.normalize("NFKD", col).encode("ascii", "ignore").decode()
    col = col.strip().lower()
    col = re.sub(r"[^a-z0-9]+", "_", col)
    return col.strip("_")

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [_slugify_column(c) for c in df.columns]
    return df

def _drop_unnamed_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[:, ~df.columns.str.contains(r"^unnamed", case=False)]

def _read_raw_csv(filename: str) -> pd.DataFrame:
    path = RAW_DIR / filename
    logger.info("Lendo '%s'...", path)
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        logger.error("Arquivo não encontrado: '%s'.", path)
        raise
    except pd.errors.EmptyDataError:
        logger.error("Arquivo '%s' está vazio ou corrompido.", path)
        raise

# ---------------------------------------------------------------------------
# Transformações por tabela
# ---------------------------------------------------------------------------

def build_dim_jogos() -> pd.DataFrame:
    df = _read_raw_csv("A - Jogos.csv")
    df = _normalize_columns(df)

    df = df.rename(columns={"jogo": "jogo_id"})

    df["ano"] = df["ano"].apply(lambda a: a + 2000 if a < 100 else a)
    df["data_jogo"] = pd.to_datetime(
        dict(year=df["ano"], month=df["mes"], day=df["dia"]), errors="coerce"
    )

    return df

def build_dim_jogadores() -> pd.DataFrame:

    df = _read_raw_csv("E - Jogadores.csv")
    df = _normalize_columns(df)
    df.insert(0, "jogador_id", range(1, len(df) + 1))
    return df

def build_fato_gols() -> pd.DataFrame:
    scored = _drop_unnamed_columns(_normalize_columns(_read_raw_csv("C - Gols Marcados.csv")))
    conceded = _drop_unnamed_columns(_normalize_columns(_read_raw_csv("D - Gols Sofridos.csv")))

    scored["tipo"] = "MARCADO"
    conceded["tipo"] = "SOFRIDO"

    fact = pd.concat([scored, conceded], ignore_index=True)
    fact = fact.rename(columns={"gol": "gol_num_original", "jogo": "jogo_id"})
    fact["data"] = pd.to_datetime(fact["data"], format="%d/%m/%Y", errors="coerce")

    fact.insert(0, "gol_id", range(1, len(fact) + 1))

    is_own_goal = fact["jogador"].str.contains(r"^\(GC\)", na=False)
    fact["gol_contra"] = is_own_goal
    fact["jogador"] = fact["jogador"].str.replace(
        r"^\(GC\)\s*", "", regex=True
    )

    return fact


def build_fato_escalacoes() -> pd.DataFrame:

    df = _read_raw_csv("B - Escalacoes.csv")
    df = _normalize_columns(df)
    df = df.rename(columns={"jogo": "jogo_id"})

    starter_cols = [c for c in df.columns if re.fullmatch(r"j\d+", c)]
    subbed_in_cols = [c for c in df.columns if re.fullmatch(r"r[1-5]", c)]
    bench_cols = [c for c in df.columns if re.fullmatch(r"r(\d+)_a", c)]

    parties = []
    for cols, papel in [
        (starter_cols, "TITULAR"),
        (subbed_in_cols, "RESERVA_ENTROU"),
        (bench_cols, "RESERVA_BANCO"),
    ]:
        part = df.melt(
            id_vars=["jogo_id"], value_vars=cols, value_name="jogador"
        ).drop(columns="variable")
        part["papel"] = papel
        parties.append(part)

    fact = pd.concat(parties, ignore_index=True)
    fact = fact.dropna(subset=["jogador"])
    fact = fact[fact["jogador"].str.strip() != ""]

    return fact.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------

def transform():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    builders = {
        "dim_jogos": build_dim_jogos,
        "dim_jogadores": build_dim_jogadores,
        "fato_gols": build_fato_gols,
        "fato_escalacoes": build_fato_escalacoes,
    }

    for name, build in builders.items():
        try:
            df = build()
            destino = PROCESSED_DIR / f"{name}.csv"
            df.to_csv(destino, index=False)
            logger.info("Salvo '%s' (%d linhas, %d colunas).", destino, *df.shape)
        except Exception:
            logger.error("Falha ao transformar/salvar '%s'.", name)
            raise