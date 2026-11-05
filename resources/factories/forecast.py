"""Builds forecast upload payloads."""

from __future__ import annotations

import uuid
from typing import Any


class ForecastFactory:
    """Builds a forecast file: one line per half-hour period, the kWh of a period growing by a fixed step through the day."""

    _periods_per_day = 48
    _header = "day,period,kwh"

    @classmethod
    def build(cls, forecast_days: list[str], kwh_step: float = 0.1) -> dict[str, Any]:
        forecast_lines = [cls._header]
        for forecast_day in forecast_days:
            for period in range(1, cls._periods_per_day + 1):
                forecast_lines.append(f"{forecast_day},{period},{kwh_step * period}")
        return {"file_name": f"forecast-{uuid.uuid4().hex[:8]}.csv", "content": "\n".join(forecast_lines) + "\n"}
