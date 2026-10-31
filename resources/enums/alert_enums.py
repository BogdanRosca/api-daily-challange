"""Alert enums."""

from enum import StrEnum


class AlertChannel(StrEnum):
    EMAIL = "EMAIL"
    SMS = "SMS"
