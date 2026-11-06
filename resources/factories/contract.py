"""Builds supply-contract payloads."""

from __future__ import annotations

from typing import Any

from resources.enums.contract_enums import ContractType


class ContractFactory:
    """Builds a contract that runs from midnight on its first day to midnight on its last, in UTC (the same day in London in winter)."""

    @classmethod
    def build(cls, first_day: str, last_day: str, contract_type: ContractType = ContractType.FIXED) -> dict[str, Any]:
        return {"contract_type": contract_type, "start_at": f"{first_day}T00:00:00+00:00", "end_at": f"{last_day}T23:59:00+00:00"}
