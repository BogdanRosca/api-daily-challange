"""Builds daily consumption reads for POST /sites/{mpan_core}/daily-reads."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal


class DailyReadFactory:
    """Builds a run of consecutive daily reads, kWh as decimal strings that rise a little each day."""

    _first_day_kwh = Decimal("35.125")
    _daily_rise_kwh = Decimal("2.250")

    @classmethod
    def build(cls, day_count: int, first_day: date | None = None) -> dict[str, str]:
        """One read a day for day_count days. Starts today unless told otherwise, so the reads are always current."""
        start_day = first_day or date.today()
        return {
            (start_day + timedelta(days=day_offset)).isoformat(): f"{cls._first_day_kwh + cls._daily_rise_kwh * day_offset:.3f}"
            for day_offset in range(day_count)
        }
