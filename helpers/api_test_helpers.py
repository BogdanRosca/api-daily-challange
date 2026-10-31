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
