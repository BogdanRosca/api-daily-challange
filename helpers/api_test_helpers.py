"""Domain helpers for the Control Room API tests. Each helper checks the status code, so tests can assert on behaviour."""

from __future__ import annotations

import logging
import uuid
from http import HTTPStatus
from typing import Any

from tenacity import retry, retry_if_exception, retry_if_exception_type, stop_after_delay, wait_fixed

from resources.constants.timeouts import (
    BILL_MONTH_BACKOFF,
    BILL_MONTH_TIMEOUT,
    EVALUATE_CONSUMPTION_BACKOFF,
    EVALUATE_CONSUMPTION_TIMEOUT,
    FORECAST_UPLOAD_BACKOFF,
    FORECAST_UPLOAD_TIMEOUT,
    TENDER_PRICING_BACKOFF,
    TENDER_PRICING_TIMEOUT,
)
from resources.dependencies.control_room_fake import ApiError, ControlRoomClient
from resources.enums.contact_enums import ContactRole
from resources.enums.contract_enums import OverlapPolicy
from resources.enums.forecast_enums import UploadStatus
from resources.enums.tender_enums import TenderStatus


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


def delete_alert_rule(api_client: ControlRoomClient, rule_id: str) -> None:
    logging.info(f"Deleting alert rule {rule_id}")
    delete_rule_response = api_client.delete_alert_rule(rule_id)
    assert delete_rule_response.status_code == HTTPStatus.NO_CONTENT, (
        f"Expected {HTTPStatus.NO_CONTENT}, got {delete_rule_response.status_code} for {rule_id}"
    )


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


def submit_daily_reads(api_client: ControlRoomClient, mpan_core: str, kwh_by_day: dict[str, str]) -> None:
    logging.info(f"Submitting {len(kwh_by_day)} daily reads for {mpan_core}")
    daily_reads_response = api_client.submit_daily_reads(mpan_core, {"reads": [{"day": day, "kwh": kwh} for day, kwh in kwh_by_day.items()]})
    assert daily_reads_response.status_code == HTTPStatus.CREATED, (
        f"Expected {HTTPStatus.CREATED}, got {daily_reads_response.status_code} for {mpan_core}"
    )


def list_consumption_days(api_client: ControlRoomClient, from_date: str, to_date: str, mpan_core: str) -> list[dict[str, Any]]:
    """The daily totals from from_date up to, but not including, to_date."""
    logging.info(f"Checking the consumption from {from_date} to {to_date}")
    consumption_response = api_client.get_consumption(from_date, to_date, mpan_core)
    assert consumption_response.status_code == HTTPStatus.OK, f"Expected {HTTPStatus.OK}, got {consumption_response.status_code} from {from_date}"
    return consumption_response.data["days"]


def _gateway_timeout(raised_exception: BaseException) -> bool:
    return isinstance(raised_exception, ApiError) and raised_exception.status_code == HTTPStatus.SERVICE_UNAVAILABLE


def bill_month(api_client: ControlRoomClient, mpan_core: str, billing_month: str, consumption_kwh: str, unit_rate: str) -> dict[str, Any]:
    """Bills one month of a site and returns the invoice. The billing gateway can time out, so a 503 is sent again."""
    idempotency_key = str(uuid.uuid4())
    logging.info(f"Billing {billing_month} for {mpan_core}: {consumption_kwh} kWh at {unit_rate}p with idempotency key {idempotency_key}")
    invoice_payload = {"billing_month": billing_month, "consumption_kwh": consumption_kwh, "unit_rate_pence_per_kwh": unit_rate}
    return _send_invoice(api_client, mpan_core, idempotency_key, invoice_payload)


@retry(
    retry=retry_if_exception(_gateway_timeout),
    stop=stop_after_delay(BILL_MONTH_TIMEOUT),
    wait=wait_fixed(BILL_MONTH_BACKOFF),
    reraise=True,
)
def _send_invoice(api_client: ControlRoomClient, mpan_core: str, idempotency_key: str, invoice_payload: dict[str, Any]) -> dict[str, Any]:
    invoice_response = api_client.create_invoice(mpan_core, invoice_payload, idempotency_key)
    assert invoice_response.status_code == HTTPStatus.CREATED, (
        f"Expected {HTTPStatus.CREATED}, got {invoice_response.status_code} for {mpan_core} and idempotency key {idempotency_key}"
    )
    return invoice_response.data


def list_site_invoices(api_client: ControlRoomClient, mpan_core: str) -> list[dict[str, Any]]:
    """Every invoice of a site, oldest billing month first."""
    logging.info(f"Checking the invoices of {mpan_core}")
    list_invoices_response = api_client.list_invoices(mpan_core)
    assert list_invoices_response.status_code == HTTPStatus.OK, f"Expected {HTTPStatus.OK}, got {list_invoices_response.status_code} for {mpan_core}"
    return list_invoices_response.data["items"]


class _UploadNotFinished(Exception):
    """The upload is still QUEUED or PROCESSING, so the wait goes on."""


def upload_forecast(api_client: ControlRoomClient, mpan_core: str, forecast_payload: dict[str, Any]) -> str:
    """Sends a forecast file and returns the upload id. Processing is asynchronous: wait_for_forecast_upload says when it is done."""
    logging.info(f"Uploading forecast file {forecast_payload['file_name']} to {mpan_core}")
    upload_response = api_client.upload_forecast(mpan_core, forecast_payload)
    assert upload_response.status_code == HTTPStatus.ACCEPTED, f"Expected {HTTPStatus.ACCEPTED}, got {upload_response.status_code} for {mpan_core}"
    return upload_response.data["upload_id"]


@retry(
    retry=retry_if_exception_type(_UploadNotFinished),
    stop=stop_after_delay(FORECAST_UPLOAD_TIMEOUT),
    wait=wait_fixed(FORECAST_UPLOAD_BACKOFF),
    reraise=True,
)
def wait_for_forecast_upload(api_client: ControlRoomClient, upload_id: str) -> dict[str, Any]:
    """Waits until the upload is PROCESSED and returns it. A FAILED upload will not fix itself, so it fails at once with the row errors."""
    upload_response = api_client.get_upload(upload_id)
    assert upload_response.status_code == HTTPStatus.OK, f"Expected {HTTPStatus.OK}, got {upload_response.status_code} for {upload_id}"
    upload_status = upload_response.data["status"]
    logging.info(f"Forecast upload {upload_id} is {upload_status}")
    assert upload_status != UploadStatus.FAILED, f"Forecast upload {upload_id} FAILED: {upload_response.data['errors']}"
    if upload_status != UploadStatus.PROCESSED:
        raise _UploadNotFinished(f"Forecast upload {upload_id} was still {upload_status} after {FORECAST_UPLOAD_TIMEOUT}s")
    return upload_response.data


def list_forecast_days(api_client: ControlRoomClient, mpan_core: str) -> list[dict[str, Any]]:
    """The forecast days stored for a site, oldest first."""
    logging.info(f"Checking the forecast of {mpan_core}")
    forecast_response = api_client.get_forecast(mpan_core)
    assert forecast_response.status_code == HTTPStatus.OK, f"Expected {HTTPStatus.OK}, got {forecast_response.status_code} for {mpan_core}"
    return forecast_response.data["forecast_days"]


def create_contract(api_client: ControlRoomClient, mpan_core: str, contract_payload: dict[str, Any]) -> dict[str, Any]:
    logging.info(f"Adding a {contract_payload['contract_type']} contract to {mpan_core}")
    create_contract_response = api_client.create_contract(mpan_core, contract_payload)
    assert create_contract_response.status_code == HTTPStatus.CREATED, (
        f"Expected {HTTPStatus.CREATED}, got {create_contract_response.status_code} for {mpan_core}"
    )
    return create_contract_response.data


def set_overlap_policy(api_client: ControlRoomClient, overlap_policy: OverlapPolicy) -> OverlapPolicy:
    """Changes the environment-wide overlap policy and returns the one it replaced."""
    previous_policy = OverlapPolicy(api_client.get_settings().data["overlap_policy"])
    logging.info(f"Changing the overlap policy from {previous_policy} to {overlap_policy}")
    update_settings_response = api_client.update_settings({"overlap_policy": overlap_policy})
    assert update_settings_response.status_code == HTTPStatus.OK, f"Expected {HTTPStatus.OK}, got {update_settings_response.status_code}"
    return previous_policy


def get_site(api_client: ControlRoomClient, mpan_core: str) -> dict[str, Any]:
    logging.info(f"Reading site {mpan_core}")
    get_site_response = api_client.get_site(mpan_core)
    assert get_site_response.status_code == HTTPStatus.OK, f"Expected {HTTPStatus.OK}, got {get_site_response.status_code} for {mpan_core}"
    return get_site_response.data


def update_site(api_client: ControlRoomClient, site: dict[str, Any], site_changes: dict[str, Any]) -> dict[str, Any]:
    """Changes some of a site's details and returns the site as it now is, ready for the next change."""
    logging.info(f"Updating {', '.join(site_changes)} of {site['mpan_core']} at version {site['version']}")
    update_site_response = api_client.patch_site(site["mpan_core"], site_changes, version=site["version"])
    assert update_site_response.status_code == HTTPStatus.OK, (
        f"Expected {HTTPStatus.OK}, got {update_site_response.status_code} for {site['mpan_core']}"
    )
    return {**site, **site_changes, "version": update_site_response.data["version"]}


def upload_hedge(api_client: ControlRoomClient, hedge_csv: str) -> dict[str, Any]:
    delivery_date = hedge_csv.splitlines()[1].split(",")[0]
    logging.info(f"Uploading the hedge for {delivery_date}")
    upload_hedge_response = api_client.upload_hedge(hedge_csv)
    assert upload_hedge_response.status_code == HTTPStatus.CREATED, (
        f"Expected {HTTPStatus.CREATED}, got {upload_hedge_response.status_code} for {delivery_date}"
    )
    return upload_hedge_response.data


class _TenderNotPriced(Exception):
    """The tender is still PENDING, so the wait goes on."""


def request_tender(api_client: ControlRoomClient, mpan_core: str, contract_months: int) -> dict[str, Any]:
    """Asks for a tender and returns it PENDING. Pricing is asynchronous: wait_for_priced_tender says when it is done."""
    logging.info(f"Requesting a {contract_months}-month tender for {mpan_core}")
    request_tender_response = api_client.request_tender(mpan_core, {"contract_months": contract_months})
    assert request_tender_response.status_code == HTTPStatus.CREATED, (
        f"Expected {HTTPStatus.CREATED}, got {request_tender_response.status_code} for {mpan_core}"
    )
    return request_tender_response.data


@retry(
    retry=retry_if_exception_type(_TenderNotPriced),
    stop=stop_after_delay(TENDER_PRICING_TIMEOUT),
    wait=wait_fixed(TENDER_PRICING_BACKOFF),
    reraise=True,
)
def wait_for_priced_tender(api_client: ControlRoomClient, tender_id: str) -> dict[str, Any]:
    """Waits until the tender is PRICED and returns it."""
    get_tender_response = api_client.get_tender(tender_id)
    assert get_tender_response.status_code == HTTPStatus.OK, f"Expected {HTTPStatus.OK}, got {get_tender_response.status_code} for {tender_id}"
    tender_status = get_tender_response.data["status"]
    logging.info(f"Tender {tender_id} is {tender_status}")
    if tender_status != TenderStatus.PRICED:
        raise _TenderNotPriced(f"Tender {tender_id} was still {tender_status} after {TENDER_PRICING_TIMEOUT}s")
    return get_tender_response.data


def create_area(api_client: ControlRoomClient, mpan_core: str, area_payload: dict[str, Any]) -> dict[str, Any]:
    logging.info(f"Adding area {area_payload['name']} to {mpan_core}")
    create_area_response = api_client.create_area(mpan_core, area_payload)
    assert create_area_response.status_code == HTTPStatus.CREATED, (
        f"Expected {HTTPStatus.CREATED}, got {create_area_response.status_code} for {mpan_core}"
    )
    return create_area_response.data


def list_site_areas(api_client: ControlRoomClient, mpan_core: str) -> list[dict[str, Any]]:
    logging.info(f"Checking the areas of {mpan_core}")
    list_areas_response = api_client.list_areas(mpan_core)
    assert list_areas_response.status_code == HTTPStatus.OK, f"Expected {HTTPStatus.OK}, got {list_areas_response.status_code} for {mpan_core}"
    return list_areas_response.data["items"]
