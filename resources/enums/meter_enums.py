"""Meter enums."""

from enum import StrEnum


class MeterType(StrEnum):
    SMART = "SMART"
    AMR = "AMR"


class MeterStatus(StrEnum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    DECOMMISSIONED = "DECOMMISSIONED"
