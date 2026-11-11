"""Builds supply-contract payloads."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any
from zoneinfo import ZoneInfo

from resources.enums.contract_enums import ContractType

london = ZoneInfo("Europe/London")


class ContractFactory:
    """Builds a contract that runs from midnight on its first day to midnight on its last, in UTC (the same day in London in winter)."""

    @classmethod
    def build(cls, first_day: str, last_day: str, contract_type: ContractType = ContractType.FIXED) -> dict[str, Any]:
        end_at = datetime.combine(date.fromisoformat(last_day), time(23, 59), tzinfo=london)
        return {"contract_type": contract_type, "start_at": f"{first_day}T00:00:00+00:00", "end_at": f"{end_at.isoformat()}"}
