"""Builds area payloads."""

from __future__ import annotations

from typing import Any


class AreaFactory:
    """Builds an area with the name it is given. Names are what the registry sorts on."""

    @classmethod
    def build(cls, name: str) -> dict[str, Any]:
        return {"name": name}
