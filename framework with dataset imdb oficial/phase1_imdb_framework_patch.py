# =============================================================================
# PHASE 1 PATCH — Adaptar o notebook do framework para o IMDb real
# SF0.25 / SF0.5 / SF1 via DuckDB
# =============================================================================
#
# Este arquivo contém os blocos de substituição para:
# - BLOCO 1 / BLOCO 2 / BLOCO 3  (dataset sintético -> IMDb real)
# - BLOCO V6                     (cardinalidade observada)
# - BLOCO V18                    (sharedness observada)
# - ajuste simples do BLOCO V22  (scale factors)
#
# Observação importante:
# Para os SFs reais, não materialize os TSVs completos em pandas.
# Use DuckDB como camada principal de consulta e só traga para DataFrame
# os resumos pequenos.
# =============================================================================


# =============================================================================
# BLOCO 1 — BUNDLE DUCKDB DO IMDb REAL
# =============================================================================
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any
import importlib.util
import subprocess
import sys
import pandas as pd

if importlib.util.find_spec("duckdb") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "duckdb"])

import duckdb


@dataclass
class IMDbDuckDBBundle:
    dataset_name: str
    scale_label: str
    sf_dir: Path
    con: Any
    raw_views: Dict[str, str] = field(default_factory=dict)
    semantic_views: Dict[str, str] = field(default_factory=dict)

    def preview(self, view_key: str, limit: int = 5) -> pd.DataFrame:
        view_name = self.raw_views.get(view_key) or self.semantic_views.get(view_key) or view_key
        return self.con.execute(f"SELECT * FROM {view_name} LIMIT {int(limit)}").df()

    def summary(self) -> pd.DataFrame:
        rows = []
        for scope, mapping in [("raw", self.raw_views), ("semantic", self.semantic_views)]:
            for alias, view_name in mapping.items():
                desc = self.con.execute(f"DESCRIBE {view_name}").df()
                rows.append({
                    "scope": scope,
                    "alias": alias,
                    "view_name": view_name,
                    "columns": desc["column_name"].tolist()
                })
        return pd.DataFrame(rows)


# =============================================================================
# BLOCO 2 — REGISTRAR OS 7 TSVs DO SCALE FACTOR COMO VIEWS DUCKDB
# =============================================================================
from pathlib import Path

# ---------------------------------------------------------
# 1) Ajuste estes caminhos no seu JupyterLab
# Cada pasta deve conter os 7 arquivos TSV exportados
# ---------------------------------------------------------
IMDB_SF_PATHS = {
    "sf0.25": Path("/SEU/CAMINHO/SF0.25"),
    "sf0.5":  Path("/SEU/CAMINHO/SF0.5"),
    "sf1":    Path("/SEU/CAMINHO/SF1"),
}

ACTIVE_SCALE_LABEL = "sf0.25"   # troque para "sf0.5" ou "sf1" quando quiser
sf_dir = IMDB_SF_PATHS[ACTIVE_SCALE_LABEL]

if not sf_dir.exists():
    raise FileNotFoundError(
        f"Pasta do scale factor não encontrada: {sf_dir}. "
        "Ajuste IMDB_SF_PATHS antes de continuar."
    )

con = duckdb.connect(database=":memory:")

# ---------------------------------------------------------
# 2) Schemas explícitos em VARCHAR
# ---------------------------------------------------------
TSV_SCHEMAS = {
    "name_basics": {
        "filename": "name.basics.tsv",
        "columns": {
            "nconst": "VARCHAR",
            "primaryName": "VARCHAR",
            "birthYear": "VARCHAR",
            "deathYear": "VARCHAR",
            "primaryProfession": "VARCHAR",
            "knownForTitles": "VARCHAR",
        },
        "max_line_size": 1_000_000,
    },
    "title_akas": {
        "filename": "title.akas.tsv",
        "columns": {
            "titleId": "VARCHAR",
            "ordering": "VARCHAR",
            "title": "VARCHAR",
            "region": "VARCHAR",
            "language": "VARCHAR",
            "types": "VARCHAR",
            "attributes": "VARCHAR",
            "isOriginalTitle": "VARCHAR",
        },
        "max_line_size": 2_000_000,
    },
    "title_basics": {
        "filename": "title.basics.tsv",
        "columns": {
            "tconst": "VARCHAR",
            "titleType": "VARCHAR",
            "primaryTitle": "VARCHAR",
            "originalTitle": "VARCHAR",
            "isAdult": "VARCHAR",
            "startYear": "VARCHAR",
            "endYear": "VARCHAR",
            "runtimeMinutes": "VARCHAR",
            "genres": "VARCHAR",
        },
        "max_line_size": 1_000_000,
    },
    "title_crew": {
        "filename": "title.crew.tsv",
        "columns": {
            "tconst": "VARCHAR",
            "directors": "VARCHAR",
            "writers": "VARCHAR",
        },
        "max_line_size": 1_000_000,
    },
    "title_episode": {
        "filename": "title.episode.tsv",
        "columns": {
            "tconst": "VARCHAR",
            "parentTconst": "VARCHAR",
            "seasonNumber": "VARCHAR",
            "episodeNumber": "VARCHAR",
        },
        "max_line_size": 1_000_000,
    },
    "title_principals": {
        "filename": "title.principals.tsv",
        "columns": {
            "tconst": "VARCHAR",
            "ordering": "VARCHAR",
            "nconst": "VARCHAR",
            "category": "VARCHAR",
            "job": "VARCHAR",
            "characters": "VARCHAR",
        },
        "max_line_size": 2_000_000,
    },
    "title_ratings": {
        "filename": "title.ratings.tsv",
        "columns": {
            "tconst": "VARCHAR",
            "averageRating": "VARCHAR",
            "numVotes": "VARCHAR",
        },
        "max_line_size": 1_000_000,
    },
}


def duckdb_columns_map_sql(columns: dict) -> str:
    return "{" + ", ".join(f"'{k}': '{v}'" for k, v in columns.items()) + "}"


def create_tsv_view(con, view_name: str, file_path: Path, columns: dict, max_line_size: int):
    file_sql = str(file_path).replace("\\", "/").replace("'", "''")
    columns_sql = duckdb_columns_map_sql(columns)

    sql = f"""
    CREATE OR REPLACE VIEW {view_name} AS
    SELECT *
    FROM read_csv(
        '{file_sql}',
        delim='\t',
        header=true,
        columns={columns_sql},
        nullstr='\\N',
        auto_detect=false,
        parallel=false,
        quote='',
        escape='',
        max_line_size={max_line_size}
    );
    """
    con.execute(sql)


raw_views = {}

for alias, spec in TSV_SCHEMAS.items():
    file_path = sf_dir / spec["filename"]
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    view_name = f"imdb_{alias}"
    create_tsv_view(
        con=con,
        view_name=view_name,
        file_path=file_path,
        columns=spec["columns"],
        max_line_size=spec["max_line_size"],
    )
    raw_views[alias] = view_name


# =============================================================================
# BLOCO 3 — DERIVAR VIEWS CONCEITUAIS COMPATÍVEIS COM O FRAMEWORK
# =============================================================================

# ---------------------------------------------------------
# 1) WatchItem como raiz conceitual
# ---------------------------------------------------------
con.execute("""
CREATE OR REPLACE VIEW imdb_watchitems AS
SELECT
    b.tconst AS watchitem_id,
    b.titleType AS title_type,
    b.primaryTitle AS title,
    b.originalTitle AS original_title,
    b.startYear AS release_year,
    b.endYear AS end_year,
    b.runtimeMinutes AS runtime_minutes,
    b.genres AS genres_raw,
    CASE
        WHEN b.genres IS NULL THEN NULL
        ELSE split_part(b.genres, ',', 1)
    END AS primary_genre,
    r.averageRating AS avg_rating,
    r.numVotes AS num_votes
FROM imdb_title_basics b
LEFT JOIN imdb_title_ratings r
    ON b.tconst = r.tconst
""")

# ---------------------------------------------------------
# 2) Persons
# ---------------------------------------------------------
con.execute("""
CREATE OR REPLACE VIEW imdb_persons AS
SELECT
    nconst AS person_id,
    primaryName AS person_name,
    birthYear AS birth_year,
    deathYear AS death_year,
    primaryProfession AS primary_profession,
    knownForTitles AS known_for_titles
FROM imdb_name_basics
""")

# ---------------------------------------------------------
# 3) Roles = linha de title.principals
# ---------------------------------------------------------
con.execute("""
CREATE OR REPLACE VIEW imdb_roles AS
SELECT
    tconst || '#' || ordering AS role_id,
    tconst AS watchitem_id,
    nconst AS person_id,
    ordering AS principal_order,
    category AS role_category,
    job,
    characters
FROM imdb_title_principals
""")

# ---------------------------------------------------------
# 4) Gêneros distintos a partir do gênero principal
# ---------------------------------------------------------
con.execute("""
CREATE OR REPLACE VIEW imdb_genres AS
SELECT DISTINCT
    primary_genre AS genre_name
FROM imdb_watchitems
WHERE primary_genre IS NOT NULL
""")

# ---------------------------------------------------------
# 5) Subtipos
# ---------------------------------------------------------
con.execute("""
CREATE OR REPLACE VIEW imdb_movies AS
SELECT
    watchitem_id,
    title,
    release_year,
    runtime_minutes,
    avg_rating,
    num_votes
FROM imdb_watchitems
WHERE title_type = 'movie'
""")

con.execute("""
CREATE OR REPLACE VIEW imdb_series AS
SELECT
    watchitem_id,
    title,
    release_year,
    end_year,
    avg_rating,
    num_votes
FROM imdb_watchitems
WHERE title_type = 'tvSeries'
""")

con.execute("""
CREATE OR REPLACE VIEW imdb_episodes AS
SELECT
    e.tconst AS watchitem_id,
    e.parentTconst AS series_watchitem_id,
    e.seasonNumber AS season_number,
    e.episodeNumber AS episode_number
FROM imdb_title_episode e
""")

semantic_views = {
    "watchitems": "imdb_watchitems",
    "persons": "imdb_persons",
    "roles": "imdb_roles",
    "genres": "imdb_genres",
    "movies": "imdb_movies",
    "series": "imdb_series",
    "episodes": "imdb_episodes",
}

imdb_data_bundle = IMDbDuckDBBundle(
    dataset_name="IMDb",
    scale_label=ACTIVE_SCALE_LABEL,
    sf_dir=sf_dir,
    con=con,
    raw_views=raw_views,
    semantic_views=semantic_views,
)

print("Resumo das views registradas:")
display(imdb_data_bundle.summary())

print("\nPrévia: watchitems")
display(imdb_data_bundle.preview("watchitems", 5))

print("\nPrévia: roles")
display(imdb_data_bundle.preview("roles", 5))

print("\nPrévia: episodes")
display(imdb_data_bundle.preview("episodes", 5))


# =============================================================================
# BLOCO V6 — CARDINALIDADE OBSERVADA NO IMDb REAL
# =============================================================================
import pandas as pd

required_names = ["imdb_data_bundle"]
for name in required_names:
    if name not in globals():
        raise NameError(f"'{name}' não está definido. Rode primeiro os blocos do IMDb real.")

con = imdb_data_bundle.con


def summarize_observed_cardinality_sql(
    con,
    rel_sql: str,
    left_col: str,
    right_col: str,
    relationship_name: str
) -> dict:
    sql = f"""
    WITH rel AS (
        SELECT
            {left_col} AS left_id,
            {right_col} AS right_id
        FROM ({rel_sql}) x
        WHERE {left_col} IS NOT NULL
          AND {right_col} IS NOT NULL
    ),
    left_to_right AS (
        SELECT left_id, COUNT(DISTINCT right_id) AS n
        FROM rel
        GROUP BY 1
    ),
    right_to_left AS (
        SELECT right_id, COUNT(DISTINCT left_id) AS n
        FROM rel
        GROUP BY 1
    )
    SELECT
        '{relationship_name}' AS relationship_name,
        '{left_col}' AS left_entity_key,
        '{right_col}' AS right_entity_key,
        (SELECT COUNT(DISTINCT left_id) FROM rel) AS left_distinct_values,
        (SELECT COUNT(DISTINCT right_id) FROM rel) AS right_distinct_values,
        ROUND((SELECT AVG(n) FROM left_to_right), 2) AS avg_right_per_left,
        (SELECT MAX(n) FROM left_to_right) AS max_right_per_left,
        ROUND((SELECT AVG(n) FROM right_to_left), 2) AS avg_left_per_right,
        (SELECT MAX(n) FROM right_to_left) AS max_left_per_right
    """
    return con.execute(sql).df().iloc[0].to_dict()


cardinality_rows = []

cardinality_rows.append(
    summarize_observed_cardinality_sql(
        con=con,
        rel_sql="""
            SELECT primary_genre, watchitem_id
            FROM imdb_watchitems
            WHERE primary_genre IS NOT NULL
        """,
        left_col="primary_genre",
        right_col="watchitem_id",
        relationship_name="Genre -- WatchItem"
    )
)

cardinality_rows.append(
    summarize_observed_cardinality_sql(
        con=con,
        rel_sql="""
            SELECT person_id, watchitem_id
            FROM imdb_roles
        """,
        left_col="person_id",
        right_col="watchitem_id",
        relationship_name="Person -- WatchItem (via Role)"
    )
)

cardinality_rows.append(
    summarize_observed_cardinality_sql(
        con=con,
        rel_sql="""
            SELECT watchitem_id, person_id
            FROM imdb_roles
        """,
        left_col="watchitem_id",
        right_col="person_id",
        relationship_name="WatchItem -- Person (via Role)"
    )
)

cardinality_rows.append(
    summarize_observed_cardinality_sql(
        con=con,
        rel_sql="""
            SELECT series_watchitem_id, watchitem_id
            FROM imdb_episodes
            WHERE series_watchitem_id IS NOT NULL
        """,
        left_col="series_watchitem_id",
        right_col="watchitem_id",
        relationship_name="Series -- Episode"
    )
)

cardinality_df = pd.DataFrame(cardinality_rows)

print("Cardinalidade observada no IMDb real:")
display(cardinality_df)


# =============================================================================
# BLOCO V18 — SHAREDNESS OBSERVADA NO IMDb REAL
# =============================================================================
import pandas as pd

required_names = ["imdb_data_bundle"]
for name in required_names:
    if name not in globals():
        raise NameError(f"'{name}' não está definido. Rode primeiro os blocos do IMDb real.")

con = imdb_data_bundle.con


def summarize_observed_sharedness_sql(
    con,
    rel_sql: str,
    root_col: str,
    target_col: str,
    root_entity: str,
    target_entity: str,
    relationship_context: str
) -> dict:
    sql = f"""
    WITH rel AS (
        SELECT
            {root_col} AS root_id,
            {target_col} AS target_id
        FROM ({rel_sql}) x
        WHERE {root_col} IS NOT NULL
          AND {target_col} IS NOT NULL
    ),
    target_to_roots AS (
        SELECT
            target_id,
            COUNT(DISTINCT root_id) AS n_roots
        FROM rel
        GROUP BY 1
    )
    SELECT
        '{root_entity}' AS root_entity,
        '{target_entity}' AS target_entity,
        '{relationship_context}' AS relationship_context,
        COUNT(*) AS n_target_instances_observed,
        ROUND(AVG(n_roots), 2) AS avg_roots_per_target,
        MAX(n_roots) AS max_roots_per_target
    FROM target_to_roots
    """
    return con.execute(sql).df().iloc[0].to_dict()


sharedness_rows = []

sharedness_rows.append(
    summarize_observed_sharedness_sql(
        con=con,
        rel_sql="""
            SELECT watchitem_id, role_id
            FROM imdb_roles
        """,
        root_col="watchitem_id",
        target_col="role_id",
        root_entity="WatchItem",
        target_entity="Role",
        relationship_context="WatchItem to Role"
    )
)

sharedness_rows.append(
    summarize_observed_sharedness_sql(
        con=con,
        rel_sql="""
            SELECT watchitem_id, person_id
            FROM imdb_roles
        """,
        root_col="watchitem_id",
        target_col="person_id",
        root_entity="WatchItem",
        target_entity="Person",
        relationship_context="WatchItem to Person via Role"
    )
)

sharedness_rows.append(
    summarize_observed_sharedness_sql(
        con=con,
        rel_sql="""
            SELECT watchitem_id, primary_genre
            FROM imdb_watchitems
            WHERE primary_genre IS NOT NULL
        """,
        root_col="watchitem_id",
        target_col="primary_genre",
        root_entity="WatchItem",
        target_entity="Genre",
        relationship_context="WatchItem to Genre"
    )
)

sharedness_rows.append(
    summarize_observed_sharedness_sql(
        con=con,
        rel_sql="""
            SELECT watchitem_id AS root_id, watchitem_id AS target_id
            FROM imdb_movies
        """,
        root_col="root_id",
        target_col="target_id",
        root_entity="WatchItem",
        target_entity="Movie",
        relationship_context="Subtype identity: Movie is WatchItem"
    )
)

sharedness_rows.append(
    summarize_observed_sharedness_sql(
        con=con,
        rel_sql="""
            SELECT watchitem_id AS root_id, watchitem_id AS target_id
            FROM imdb_series
        """,
        root_col="root_id",
        target_col="target_id",
        root_entity="WatchItem",
        target_entity="Series",
        relationship_context="Subtype identity: Series is WatchItem"
    )
)

sharedness_rows.append(
    summarize_observed_sharedness_sql(
        con=con,
        rel_sql="""
            SELECT watchitem_id AS root_id, watchitem_id AS target_id
            FROM imdb_episodes
        """,
        root_col="root_id",
        target_col="target_id",
        root_entity="WatchItem",
        target_entity="Episode",
        relationship_context="Subtype identity: Episode is WatchItem"
    )
)

sharedness_rows.append(
    summarize_observed_sharedness_sql(
        con=con,
        rel_sql="""
            SELECT series_watchitem_id, watchitem_id
            FROM imdb_episodes
            WHERE series_watchitem_id IS NOT NULL
        """,
        root_col="series_watchitem_id",
        target_col="watchitem_id",
        root_entity="Series",
        target_entity="Episode",
        relationship_context="Series to Episode (containment-like)"
    )
)

sharedness_df = pd.DataFrame(sharedness_rows)

print("Sharedness observada no IMDb real:")
display(sharedness_df)


# =============================================================================
# AJUSTE DO BLOCO V22 — SCALE FACTORS CORRETOS
# =============================================================================
import pandas as pd

mongo_scale_factors_df = pd.DataFrame([
    {
        "scale_factor": 0.25,
        "scale_label": "sf0.25",
        "execution_phase": "current"
    },
    {
        "scale_factor": 0.50,
        "scale_label": "sf0.5",
        "execution_phase": "current"
    },
    {
        "scale_factor": 1.00,
        "scale_label": "sf1",
        "execution_phase": "current"
    }
])

print("Scale factors planejados:")
display(mongo_scale_factors_df)
