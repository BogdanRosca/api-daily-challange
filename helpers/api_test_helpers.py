"""Domain helpers for the Control Room API tests. Each helper checks the status code, so tests can assert on behaviour."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any

from tenacity import retry, retry_if_exception, stop_after_delay, wait_fixed

from resources.constants.timeouts import EVALUATE_CONSUMPTION_BACKOFF, EVALUATE_CONSUMPTION_TIMEOUT
from resources.dependencies.control_room_fake import ApiError, ControlRoomClient
from resources.enums.contact_enums import ContactRole


def create_contact(api_client: ControlRoomClient, mpan_core: str, contact_payload: dict[str, Any]) -> dict[str, Any]:
    logging.info(f"Adding a {contact_payload['role']} contact to {mpan_core}")
    create_contact_response = api_client.create_contact(mpan_core, contact_payload)
    assert create_contact_response.status_code == HTTPStatus.CREATED, (
        f"Expected {HTTPStatus.CREATED}, got {create_contact_response.status_code} for {mpan_core}"
    )
    return create_contact_response.data


def update_contact(api_client: ControlRoomClient, contact: dict[str, Any], contact_changes: dict[str, Any]) -> dict[str, Any]:
    """Changes some of a contact's details and leaves the rest as they are."""
    logging.info(f"Updating {', '.join(contact_changes)} of {contact['id']}")
    update_contact_response = api_client.patch_contact(contact["id"], contact_changes)
    assert update_contact_response.status_code == HTTPStatus.OK, (
        f"Expected {HTTPStatus.OK}, got {update_contact_response.status_code} for {contact['id']}"
    )
    return update_contact_response.data


def list_site_contacts(api_client: ControlRoomClient, mpan_core: str, role: ContactRole | None = None) -> list[dict[str, Any]]:
    logging.info(f"Checking the {role or 'all'} contacts of {mpan_core}")
    list_contacts_response = api_client.list_contacts(mpan_core, role=role)
    assert list_contacts_response.status_code == HTTPStatus.OK, f"Expected {HTTPStatus.OK}, got {list_contacts_response.status_code} for {mpan_core}"
    return list_contacts_response.data["items"]


def create_alert_rule(api_client: ControlRoomClient, mpan_core: str, alert_rule_payload: dict[str, Any]) -> dict[str, Any]:
    logging.info(f"Adding alert rule {alert_rule_payload['name']} to {mpan_core}")
    create_rule_response = api_client.create_alert_rule(mpan_core, alert_rule_payload)
    assert create_rule_response.status_code == HTTPStatus.CREATED, (
        f"Expected {HTTPStatus.CREATED}, got {create_rule_response.status_code} for {mpan_core}"
    )
    return create_rule_response.data


def _too_many_requests(raised_exception: BaseException) -> bool:
    return isinstance(raised_exception, ApiError) and raised_exception.status_code == HTTPStatus.TOO_MANY_REQUESTS


@retry(
    retry=retry_if_exception(_too_many_requests),
    stop=stop_after_delay(EVALUATE_CONSUMPTION_TIMEOUT),
    wait=wait_fixed(EVALUATE_CONSUMPTION_BACKOFF),
    reraise=True,
)
def evaluate_day(api_client: ControlRoomClient, mpan_core: str, day: str, kwh: str) -> list[str]:
    """Sends one day's consumption for evaluation and returns the ids of the rules it triggered."""
    logging.info(f"Evaluating {kwh} kWh on {day} for {mpan_core}")
    evaluation_response = api_client.evaluate_consumption(mpan_core, {"day": day, "kwh": kwh})
    assert evaluation_response.status_code == HTTPStatus.CREATED, (
        f"Expected {HTTPStatus.CREATED}, got {evaluation_response.status_code} for {mpan_core} on {day}"
    )
    return evaluation_response.data["triggered_rule_ids"]


def list_site_alerts(api_client: ControlRoomClient, mpan_core: str) -> list[dict[str, Any]]:
    """Every alert of a site, following the cursor until the last page."""
    logging.info(f"Checking the alerts of {mpan_core}")
    site_alerts: list[dict[str, Any]] = []
    next_cursor: str | None = None
    while True:
        alerts_page_response = api_client.list_alerts(mpan_core, cursor=next_cursor)
        assert alerts_page_response.status_code == HTTPStatus.OK, f"Expected {HTTPStatus.OK}, got {alerts_page_response.status_code} for {mpan_core}"
        site_alerts.extend(alerts_page_response.data["items"])
        next_cursor = alerts_page_response.data["next_cursor"]
        if next_cursor is None:
            return site_alerts


def register_meter(api_client: ControlRoomClient, mpan_core: str, meter_payload: dict[str, Any]) -> dict[str, Any]:
    logging.info(f"Registering meter {meter_payload['serial_number']} at {mpan_core}")
    register_meter_response = api_client.register_meter(mpan_core, meter_payload)
    assert register_meter_response.status_code == HTTPStatus.CREATED, (
        f"Expected {HTTPStatus.CREATED}, got {register_meter_response.status_code} for {mpan_core}"
    )
    return register_meter_response.data


def list_site_meters(api_client: ControlRoomClient, mpan_core: str) -> list[dict[str, Any]]:
    """Every meter of a site in registration order, following the cursor until the last page."""
    logging.info(f"Checking the meters of {mpan_core}")
    site_meters: list[dict[str, Any]] = []
    next_cursor: str | None = None
    while True:
        meters_page_response = api_client.list_meters(mpan_core, cursor=next_cursor)
        assert meters_page_response.status_code == HTTPStatus.OK, f"Expected {HTTPStatus.OK}, got {meters_page_response.status_code} for {mpan_core}"
        site_meters.extend(meters_page_response.data["items"])
        next_cursor = meters_page_response.data["next_cursor"]
        if next_cursor is None:
            return site_meters


def submit_meter_reading(api_client: ControlRoomClient, meter_id: str, read_at: str, register_kwh: str) -> dict[str, Any]:
    logging.info(f"Submitting {register_kwh} kWh read on {read_at} for {meter_id}")
    submit_reading_response = api_client.submit_reading(meter_id, {"read_at": read_at, "register_kwh": register_kwh})
    assert submit_reading_response.status_code == HTTPStatus.CREATED, (
        f"Expected {HTTPStatus.CREATED}, got {submit_reading_response.status_code} for {meter_id} on {read_at}"
    )
    return submit_reading_response.data
