"""Builds hedge upload files."""

from __future__ import annotations

from datetime import datetime, timedelta


class HedgeFactory:
    """Builds a hedge CSV for one delivery day: one row per half-hour settlement period, each hedging the same volume."""

    _MARCH = 3
    _OCTOBER = 10
    _SUNDAY = 6
    _periods_per_day = 48
    _header = "delivery_date,settlement_period,volume_mwh"

    @classmethod
    def build(cls, delivery_date: str, volume_mwh: str = "0.500") -> str:

        date_obj = datetime.strptime(delivery_date, "%Y-%m-%d")

        if cls._is_uk_clock_change_day(date_obj) is True:
            if date_obj.month == cls._MARCH:
                cls._periods_per_day = 46
            else:
                cls._periods_per_day = 50

        hedge_lines = [cls._header]
        for settlement_period in range(1, cls._periods_per_day + 1):
            hedge_lines.append(f"{delivery_date},{settlement_period},{volume_mwh}")
        return "\n".join(hedge_lines) + "\n"

    @classmethod
    def _is_uk_clock_change_day(cls, delivery_date: datetime) -> bool:

        if delivery_date.month not in [cls._MARCH, cls._OCTOBER]:
            return False

        if delivery_date.weekday() is not cls._SUNDAY:
            return False

        if cls._is_last_sunday_of_month(delivery_date):
            return True

        return False

    @classmethod
    def _is_last_sunday_of_month(cls, delivery_date: datetime) -> bool:
        next_week = delivery_date + timedelta(days=7)
        return next_week.month != delivery_date.month
