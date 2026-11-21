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
        return cls._build_csv(delivery_date, [volume_mwh] * cls._period_count(delivery_date))

    @classmethod
    def build_for_day_volume(cls, delivery_date: str, day_volume_mwh: str) -> str:
        """Builds a hedge for one day's traded volume in whole kWh: periods differ by at most 1 kWh and add up to exactly the traded volume."""
        period_count = cls._period_count(delivery_date)
        day_volume_kwh = int(Decimal(day_volume_mwh) / cls._volume_step_mwh)
        base_period_kwh, leftover_kwh = divmod(day_volume_kwh, period_count)
        period_volumes_mwh = [
            f"{(base_period_kwh + (1 if period_index < leftover_kwh else 0)) * cls._volume_step_mwh}" for period_index in range(period_count)
        ]
        return cls._build_csv(delivery_date, period_volumes_mwh)

    @classmethod
    def _build_csv(cls, delivery_date: str, period_volumes_mwh: list[str]) -> str:
        hedge_lines = [cls._header]
        for settlement_period, volume_mwh in enumerate(period_volumes_mwh, start=1):
            hedge_lines.append(f"{delivery_date},{settlement_period},{volume_mwh}")
        return "\n".join(hedge_lines) + "\n"

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
