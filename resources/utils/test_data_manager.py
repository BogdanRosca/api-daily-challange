"""
The site pool. In the real repo this is the DynamoDB MPANs table seeded from resources/data/site_data.json; here it reads the file.

A test that needs a site takes the next unused one from the pool, so no two tests touch the same site. A test that needs
a particular, named site asks for it from resources/data/fixed_sites.json instead, and shares it with every other test
that does.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from resources.enums.site_enums import SiteType


@dataclass(frozen=True)
class SiteData:
    mpan: str
    site_type: SiteType


class DataLocked(Exception):
    pass


class DataManager:
    """Hands out unused pool sites. One instance per session; `_claimed` stands in for the DynamoDB conditional claim."""

    _data_dir = Path(__file__).resolve().parent.parent / "data"

    def __init__(self) -> None:
        self._pool_entries: list[dict[str, Any]] = json.loads((self._data_dir / "site_data.json").read_text())
        self._fixed_entries: list[dict[str, Any]] = json.loads((self._data_dir / "fixed_sites.json").read_text())
        self._claimed: set[str] = set()

    def get_next_available_site(self, *, site_type: SiteType | None = None) -> SiteData:
        """Retrieve the next unused pool site.

        :param site_type: filter by site type, None for any.
        :raises DataLocked: if no unused site is available.
        """
        for pool_entry in self._pool_entries:
            if pool_entry["mpan"] in self._claimed or (site_type and pool_entry["site_type"] != site_type):
                continue
            self._claimed.add(pool_entry["mpan"])
            logging.info(f"Claimed pool site {pool_entry['mpan']} ({pool_entry['site_type']})")
            return SiteData(mpan=pool_entry["mpan"], site_type=SiteType(pool_entry["site_type"]))
        raise DataLocked(f"No more unused sites available for site_type={site_type}")

    def get_fixed_site(self, site_name: str) -> SiteData:
        """A named site from fixed_sites.json. Shared: every test that asks for it gets the same one."""
        for fixed_entry in self._fixed_entries:
            if fixed_entry["name"] == site_name:
                return SiteData(mpan=fixed_entry["mpan"], site_type=SiteType(fixed_entry["site_type"]))
        raise KeyError(f"No fixed site named {site_name}")
