"""Tender enums."""

from enum import StrEnum


class TenderStatus(StrEnum):
    PENDING = "PENDING"
    PRICED = "PRICED"
