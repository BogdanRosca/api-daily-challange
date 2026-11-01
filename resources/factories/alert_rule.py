"""Builds alert rule payloads."""

from __future__ import annotations

import uuid
from typing import Any

from resources.enums.alert_enums import AlertChannel


class AlertRuleFactory:
    """Builds an alert rule nobody else uses: a unique name and a decimal-string threshold."""

    @classmethod
    def build(cls, threshold_kwh: str = "100.000", channel: AlertChannel = AlertChannel.EMAIL) -> dict[str, Any]:
        return {"name": f"QA Rule {uuid.uuid4().hex[:8]}", "threshold_kwh": threshold_kwh, "channel": channel.value}
