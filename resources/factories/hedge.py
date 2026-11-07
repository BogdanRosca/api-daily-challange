"""Builds hedge upload files."""

from __future__ import annotations


class HedgeFactory:
    """Builds a hedge CSV for one delivery day: one row per half-hour settlement period, each hedging the same volume."""

    _periods_per_day = 48
    _header = "delivery_date,settlement_period,volume_mwh"

    @classmethod
    def build(cls, delivery_date: str, volume_mwh: str = "0.500") -> str:
        hedge_lines = [cls._header]
        for settlement_period in range(1, cls._periods_per_day + 1):
            hedge_lines.append(f"{delivery_date},{settlement_period},{volume_mwh}")
        return "\n".join(hedge_lines) + "\n"
