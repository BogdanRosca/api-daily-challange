"""Domain helpers for the Control Room API tests. Each helper checks the status code, so tests can assert on behaviour."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any

from resources.dependencies.control_room_fake import ControlRoomClient
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
