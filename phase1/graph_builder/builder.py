from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd

from phase1.ontology import schema
from phase1.utils import ids


def build_nodes(long_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    countries = (
        long_df[["country_name", "country_code"]]
        .drop_duplicates()
        .assign(
            id=lambda df: df["country_code"].map(ids.country_id),
            label=schema.COUNTRY_LABEL,
        )
        .rename(columns={"country_name": "name", "country_code": "code"})
    )

    indicators = (
        long_df[["indicator_name", "indicator_code"]]
        .drop_duplicates()
        .assign(
            id=lambda df: df["indicator_code"].map(ids.indicator_id),
            label=schema.INDICATOR_LABEL,
        )
        .rename(columns={"indicator_name": "name", "indicator_code": "code"})
    )

    years = (
        long_df[["year"]]
        .drop_duplicates()
        .assign(
            id=lambda df: df["year"].map(ids.year_id),
            label=schema.YEAR_LABEL,
        )
        .rename(columns={"year": "value"})
    )

    observations = (
        long_df[["country_code", "indicator_code", "year", "value"]]
        .assign(
            id=lambda df: df.apply(
                lambda row: ids.observation_id(
                    row["country_code"], row["indicator_code"], row["year"]
                ),
                axis=1,
            ),
            label=schema.OBSERVATION_LABEL,
        )
        .drop_duplicates(subset=["id"])
    )

    return {
        schema.COUNTRY_LABEL: countries,
        schema.INDICATOR_LABEL: indicators,
        schema.YEAR_LABEL: years,
        schema.OBSERVATION_LABEL: observations,
    }


def build_relationships(long_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    observations = long_df.assign(
        observation_id=lambda df: df.apply(
            lambda row: ids.observation_id(
                row["country_code"], row["indicator_code"], row["year"]
            ),
            axis=1,
        ),
        country_id=lambda df: df["country_code"].map(ids.country_id),
        indicator_id=lambda df: df["indicator_code"].map(ids.indicator_id),
        year_id=lambda df: df["year"].map(ids.year_id),
    )

    has_observation = observations[["country_id", "observation_id"]].drop_duplicates()
    has_observation = has_observation.rename(
        columns={"country_id": "start_id", "observation_id": "end_id"}
    )

    of_indicator = observations[["observation_id", "indicator_id"]].drop_duplicates()
    of_indicator = of_indicator.rename(
        columns={"observation_id": "start_id", "indicator_id": "end_id"}
    )

    at_year = observations[["observation_id", "year_id"]].drop_duplicates()
    at_year = at_year.rename(columns={"observation_id": "start_id", "year_id": "end_id"})

    return {
        schema.REL_HAS_OBSERVATION: has_observation,
        schema.REL_OF_INDICATOR: of_indicator,
        schema.REL_AT_YEAR: at_year,
    }


def build_graph(long_df: pd.DataFrame) -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    nodes = build_nodes(long_df)
    rels = build_relationships(long_df)
    return nodes, rels
