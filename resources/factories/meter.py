"""Builds meter registration payloads."""

from __future__ import annotations

import uuid
from typing import Any

from resources.enums.meter_enums import MeterType


class MeterFactory:
    """Builds a meter nobody else uses: serial numbers are unique across the whole QA environment."""

    _base_payload: dict[str, Any] = {"serial_number": "", "meter_type": MeterType.SMART.value, "install_date": "2026-01-15"}

    @classmethod
    def build(cls, meter_type: MeterType = MeterType.SMART) -> dict[str, Any]:
        meter_payload = cls._base_payload
        meter_payload["serial_number"] = f"QA-{uuid.uuid4().hex[:10]}"
        meter_payload["meter_type"] = meter_type.value
        return meter_payload
