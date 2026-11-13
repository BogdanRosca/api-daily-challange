"""Root fixtures: credentials, auth, API client, test-data allocation."""

from __future__ import annotations

from collections.abc import Iterator
from http import HTTPStatus
from typing import Any

import pytest

from helpers.api_test_helpers import create_alert_rule, delete_alert_rule, set_overlap_policy
from resources.dependencies.control_room_fake import ENV, ApiError, ControlRoomClient
from resources.enums.contract_enums import OverlapPolicy
from resources.enums.site_enums import SiteType
from resources.factories.alert_rule import AlertRuleFactory
from resources.utils.config_manager import ConfigManager, UserCredentials
from resources.utils.test_data_manager import DataManager, SiteData


@pytest.fixture(scope="session")
def credentials() -> UserCredentials:
    return ConfigManager().user_credentials()


@pytest.fixture(scope="function")
def bearer_token(credentials: UserCredentials) -> str:
    """A fresh token per test: a token is good for 25 requests, so one shared by the whole run would expire part-way."""
    return ENV.login(credentials.default_email, credentials.default_password)


@pytest.fixture(scope="function")
def api_client(bearer_token: str) -> Iterator[ControlRoomClient]:
    yield ControlRoomClient(ENV, bearer_token)


@pytest.fixture(scope="session")
def data_manager() -> DataManager:
    return DataManager()


@pytest.fixture(scope="function")
def site_type(request: pytest.FixtureRequest) -> SiteType | None:
    """Which kind of site a test draws from the pool. Tests set it with `parametrize(..., indirect=True)`; None means any."""
    return getattr(request, "param", None)


@pytest.fixture(scope="function")
def unique_site(data_manager: DataManager, site_type: SiteType | None) -> SiteData:
    return data_manager.get_next_available_site(site_type=site_type)


@pytest.fixture(scope="function")
def overlaps_allowed(api_client: ControlRoomClient) -> Iterator[None]:
    """Lets a test create overlapping contracts. The overlap policy is shared by the whole environment."""
    set_overlap_policy(api_client, OverlapPolicy.ALLOW)
    yield
    set_overlap_policy(api_client, OverlapPolicy.REJECT)


@pytest.fixture(scope="function")
def alert_rule(api_client: ControlRoomClient, unique_site: SiteData) -> Iterator[dict[str, Any]]:
    """An EMAIL rule on the test's site that fires above 100 kWh. Deleted in teardown, so it never alerts on anything after the test."""
    created_rule = create_alert_rule(api_client, unique_site.mpan, AlertRuleFactory.build(threshold_kwh="100.000"))
    yield created_rule
    try:
        delete_alert_rule(api_client, created_rule["id"])
    except ApiError as returned_error:
        assert returned_error.status_code == HTTPStatus.NOT_FOUND, f"Deleting alert rule failed with {returned_error.status_code} status code"
