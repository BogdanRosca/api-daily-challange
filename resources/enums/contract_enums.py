"""Supply-contract enums."""

from enum import StrEnum


class ContractType(StrEnum):
    FIXED = "FIXED"
    FLEX = "FLEX"


class OverlapPolicy(StrEnum):
    REJECT = "REJECT"
    ALLOW = "ALLOW"
