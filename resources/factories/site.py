"""Builds site change payloads for PATCH /sites/{mpan_core}."""

from __future__ import annotations

import uuid
from typing import Any
import copy


class SiteFactory:
    """Builds the changes that onboard a site: the tags every managed site carries, its own tags and a contact email nobody else uses."""

    _onboarding_changes: dict[str, Any] = {"tags": ["half-hourly", "qa-managed"], "contact_email": ""}

    @classmethod
    def build_onboarding(cls, *site_tags: str) -> dict[str, Any]:
        onboarding_changes = copy.deepcopy(cls._onboarding_changes)
        onboarding_changes["contact_email"] = f"qa.site.{uuid.uuid4().hex[:8]}@example.com"
        onboarding_changes["tags"] = list(dict.fromkeys([*onboarding_changes["tags"], *site_tags]))
        return onboarding_changes
