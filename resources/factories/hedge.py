"""Builds hedge upload files."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal


class HedgeFactory:
    """Builds a hedge CSV for one delivery day: one row per half-hour settlement period, each hedging the same volume."""

    _MARCH = 3
    _OCTOBER = 10
    _SUNDAY = 6
    _periods_per_day = 48
    _header = "delivery_date,settlement_period,volume_mwh"
    _volume_step_mwh = Decimal("0.001")

    @classmethod
    def build(cls, delivery_date: str, volume_mwh: str = "0.500") -> str:
        hedge_lines = [cls._header]
        for settlement_period in range(1, cls._period_count(delivery_date) + 1):
            hedge_lines.append(f"{delivery_date},{settlement_period},{volume_mwh}")
        return "\n".join(hedge_lines) + "\n"

    @classmethod
    def build_for_day_volume(cls, delivery_date: str, day_volume_mwh: str) -> str:
        """Builds a hedge for one day's traded volume, spread evenly over the day's settlement periods to the nearest kWh."""
        period_volume_mwh = (Decimal(day_volume_mwh) / cls._period_count(delivery_date)).quantize(cls._volume_step_mwh)
        return cls.build(delivery_date, f"{period_volume_mwh}")

    @classmethod
    def _period_count(cls, delivery_date: str) -> int:
        date_obj = datetime.strptime(delivery_date, "%Y-%m-%d")
        if cls._is_uk_clock_change_day(date_obj):
            return 46 if date_obj.month == cls._MARCH else 50
        return cls._periods_per_day

    @classmethod
    def _is_uk_clock_change_day(cls, delivery_date: datetime) -> bool:

        if delivery_date.month not in [cls._MARCH, cls._OCTOBER]:
            return False

        if delivery_date.weekday() != cls._SUNDAY:
            return False

        if cls._is_last_sunday_of_month(delivery_date):
            return True

        return False

    @classmethod
    def _is_last_sunday_of_month(cls, delivery_date: datetime) -> bool:
        next_week = delivery_date + timedelta(days=7)
        return next_week.month != delivery_date.month
