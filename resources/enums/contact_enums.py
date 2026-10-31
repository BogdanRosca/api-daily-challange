"""Site-contact enums."""

from enum import StrEnum


class ContactRole(StrEnum):
    PRIMARY = "PRIMARY"
    BILLING = "BILLING"
    OPERATIONS = "OPERATIONS"
