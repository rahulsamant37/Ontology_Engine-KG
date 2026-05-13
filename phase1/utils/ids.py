from __future__ import annotations


def country_id(country_code: str) -> str:
    return f"country::{country_code}"


def indicator_id(indicator_code: str) -> str:
    return f"indicator::{indicator_code}"


def year_id(year: int) -> str:
    return f"year::{year}"


def observation_id(country_code: str, indicator_code: str, year: int) -> str:
    return f"observation::{country_code}::{indicator_code}::{year}"
