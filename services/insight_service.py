from __future__ import annotations

from models.schemas import Insight


class InsightService:
    def synthesize(self, question: str, drivers: list[str], confidence: float) -> Insight:
        lead = drivers[:3]
        explanation = "The engine linked policy, inflation, and market signals from ingested evidence."
        impact = [
            "Equity valuation sensitivity may increase",
            "Bond-equity cross-asset volatility can rise",
            "Macro risk monitoring should prioritize inflation and policy commentary",
        ]

        insight_text = (
            f"For question '{question}', the most relevant macro drivers are: "
            + ", ".join(lead if lead else ["limited evidence"])
            + "."
        )

        return Insight(
            insight=insight_text,
            confidence=confidence,
            drivers=drivers,
            explanation=explanation,
            impact=impact,
        )
