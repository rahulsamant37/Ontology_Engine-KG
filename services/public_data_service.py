from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


@dataclass(frozen=True)
class IndicatorDefinition:
    code: str
    name: str
    unit: str
    event_type: str


DEFAULT_INDICATORS: tuple[IndicatorDefinition, ...] = (
    IndicatorDefinition("FP.CPI.TOTL.ZG", "Inflation (CPI, annual %)", "%", "inflation_update"),
    IndicatorDefinition("FR.INR.LEND", "Lending interest rate", "%", "monetary_policy"),
    IndicatorDefinition("CM.MKT.LCAP.CD", "Market capitalization (USD)", "USD", "market_movement"),
    IndicatorDefinition("NY.GDP.MKTP.CD", "Crude oil price index", "index", "commodity_price_move"),
)


class PublicDataService:
    """Fetches structured macro indicators from the World Bank API."""

    base_url = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"

    def fetch_structured_events(
        self,
        country_code: str,
        start_year: int,
        end_year: int,
        indicators: list[str] | None = None,
    ) -> list[dict]:
        requested = set(indicators or [])
        definitions = [
            definition
            for definition in DEFAULT_INDICATORS
            if not requested or definition.code in requested
        ]

        events: list[dict] = []
        for definition in definitions:
            series = self._fetch_indicator_series(
                country_code=country_code,
                indicator_code=definition.code,
                start_year=start_year,
                end_year=end_year,
            )
            for point in series:
                if point["value"] is None:
                    continue

                # Some World Bank points can contain non-numeric placeholders.
                try:
                    metric_value = float(point["value"])
                except (TypeError, ValueError):
                    continue

                date_raw = point.get("date")
                if date_raw is None:
                    continue

                try:
                    year = int(date_raw)
                except (TypeError, ValueError):
                    continue

                title = f"{definition.name} update for {country_code.upper()} ({year})"
                text = (
                    f"{definition.name} for {country_code.upper()} in {year} was "
                    f"{metric_value} {definition.unit}."
                )
                events.append(
                    {
                        "source": f"world_bank:{definition.code}",
                        "payload_type": "structured",
                        "payload": {
                            "title": title,
                            "text": text,
                            "event_type": definition.event_type,
                            "country": country_code.upper(),
                            "timestamp": f"{year}-12-31T00:00:00+00:00",
                            "metrics": [
                                {
                                    "name": definition.name,
                                    "value": metric_value,
                                    "unit": definition.unit,
                                    "period": str(year),
                                }
                            ],
                            "tags": ["public_api", "world_bank", definition.event_type],
                            "entities": [country_code.upper(), definition.name],
                        },
                    }
                )
        return events

    def _fetch_indicator_series(
        self,
        country_code: str,
        indicator_code: str,
        start_year: int,
        end_year: int,
    ) -> list[dict]:
        params = urlencode(
            {
                "format": "json",
                "date": f"{start_year}:{end_year}",
                "per_page": 200,
            }
        )
        url = self.base_url.format(country=country_code.lower(), indicator=indicator_code)
        request_url = f"{url}?{params}"

        try:
            with urlopen(request_url, timeout=15) as response:
                body = response.read().decode("utf-8")
        except (HTTPError, URLError) as exc:
            msg = (
                "World Bank API fetch failed for "
                f"country={country_code} indicator={indicator_code}: {exc}"
            )
            raise RuntimeError(msg) from exc

        payload = json.loads(body)
        if not isinstance(payload, list) or len(payload) < 2:
            msg = (
                "Unexpected World Bank response format for "
                f"country={country_code} indicator={indicator_code}"
            )
            raise RuntimeError(msg)

        series = payload[1]
        if not isinstance(series, list):
            return []
        return series
