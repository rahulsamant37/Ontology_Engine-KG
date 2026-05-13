from __future__ import annotations

from typing import List

import pandas as pd


def detect_year_columns(df: pd.DataFrame) -> List[str]:
    return [col for col in df.columns if col.isdigit()]


def wide_to_long(df: pd.DataFrame, id_columns: List[str]) -> pd.DataFrame:
    year_columns = detect_year_columns(df)
    long_df = df.melt(
        id_vars=id_columns,
        value_vars=year_columns,
        var_name="Year",
        value_name="Value",
    )

    long_df["Year"] = pd.to_numeric(long_df["Year"], errors="coerce")
    long_df["Value"] = pd.to_numeric(long_df["Value"], errors="coerce")

    long_df = long_df.dropna(subset=["Year", "Value"])
    long_df["Year"] = long_df["Year"].astype(int)

    long_df = long_df.rename(
        columns={
            "Country Name": "country_name",
            "Country Code": "country_code",
            "Indicator Name": "indicator_name",
            "Indicator Code": "indicator_code",
            "Year": "year",
            "Value": "value",
        }
    )

    return long_df
