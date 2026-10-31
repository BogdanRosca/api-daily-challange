"""Site enums. In the real repo: resources/enums/site_enums.py."""

from enum import StrEnum


class SiteType(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class SiteStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
