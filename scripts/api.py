"""
Calls the Control Room fake directly: status, body and the environment's log of that one call.

    python scripts/api.py GET /sites/1300123456718
    python scripts/api.py POST /sites/1300123456718/contacts '{"name": "Ada", "email": "ada@example.com", "role": "PRIMARY"}'
    python scripts/api.py PATCH /sites/1300123456718 '{"tags": ["cold-store"]}' --if-match 1001
    python scripts/api.py GET '/consumption?from_date=2026-11-01&to_date=2026-12-01'

Each run starts from a clean environment (like each pytest run), so chain calls with --then:

    python scripts/api.py POST /sites/1300123456718/meters '{"serial_number": "QA1", "meter_type": "SMART", "install_date": "2026-10-01"}' \\
        --then GET /sites/1300123456718/meters
"""

from __future__ import annotations

import json
import logging
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from resources.dependencies.control_room_fake import ENV, ApiError, ControlRoomClient, Response  # noqa: E402


class ApiCli:
    """Maps METHOD /path to the client call the generated client would make."""

    _routes: tuple[tuple[str, str, str], ...] = (
        ("GET", r"/settings", "get_settings"),
        ("PATCH", r"/settings", "update_settings"),
        ("GET", r"/sites", "list_sites"),
        ("GET", r"/sites/(\d{13})", "get_site"),
        ("PATCH", r"/sites/(\d{13})", "patch_site"),
        ("POST", r"/sites/(\d{13})/deactivation", "deactivate_site"),
        ("POST", r"/sites/(\d{13})/areas", "create_area"),
        ("GET", r"/sites/(\d{13})/areas", "list_areas"),
        ("POST", r"/sites/(\d{13})/tenders", "request_tender"),
        ("GET", r"/tenders/([\w-]+)", "get_tender"),
        ("POST", r"/hedges", "upload_hedge"),
        ("GET", r"/hedges/([\w-]+)", "get_hedge"),
        ("POST", r"/sites/(\d{13})/invoices", "create_invoice"),
        ("GET", r"/sites/(\d{13})/invoices", "list_invoices"),
        ("POST", r"/sites/(\d{13})/forecast-uploads", "upload_forecast"),
        ("GET", r"/forecast-uploads/([\w-]+)", "get_upload"),
        ("GET", r"/sites/(\d{13})/forecast", "get_forecast"),
        ("POST", r"/sites/(\d{13})/contracts", "create_contract"),
        ("GET", r"/sites/(\d{13})/contracts", "list_contracts"),
        ("POST", r"/sites/(\d{13})/contacts", "create_contact"),
        ("GET", r"/sites/(\d{13})/contacts", "list_contacts"),
        ("PUT", r"/contacts/([\w-]+)", "replace_contact"),
        ("PATCH", r"/contacts/([\w-]+)", "patch_contact"),
        ("DELETE", r"/contacts/([\w-]+)", "delete_contact"),
        ("POST", r"/sites/(\d{13})/daily-reads", "submit_daily_reads"),
        ("GET", r"/consumption", "get_consumption"),
        ("GET", r"/sites/(\d{13})/consumption-summary", "get_monthly_summary"),
        ("POST", r"/sites/(\d{13})/alert-rules", "create_alert_rule"),
        ("GET", r"/alert-rules/([\w-]+)", "get_alert_rule"),
        ("DELETE", r"/alert-rules/([\w-]+)", "delete_alert_rule"),
        ("POST", r"/sites/(\d{13})/evaluations", "evaluate_consumption"),
        ("GET", r"/sites/(\d{13})/alerts", "list_alerts"),
        ("POST", r"/sites/(\d{13})/meters", "register_meter"),
        ("GET", r"/sites/(\d{13})/meters", "list_meters"),
        ("POST", r"/meters/([\w-]+)/readings", "submit_reading"),
        ("GET", r"/meters/([\w-]+)/readings", "list_readings"),
    )
    _raw_body_operations = ("upload_hedge",)

    def __init__(self) -> None:
        self._client = ControlRoomClient(ENV, ENV.login("automation@example.com", "not-the-real-one"))

    def call(self, method: str, url: str, body_text: str | None, options: dict[str, str]) -> int:
        path, _, query_string = url.partition("?")
        query_params = dict(parse_qsl(query_string))
        route = self._match(method, path)
        if route is None:
            print(f"api: no operation for {method} {path}; the paths are in resources/openapi/control_room_admin.json")
            return 2
        operation_name, path_values = route
        operation: Callable[..., Response] = getattr(self._client, operation_name)
        call_args: list[Any] = list(path_values)
        if body_text is not None:
            call_args.append(body_text.replace("\\n", "\n") if operation_name in self._raw_body_operations else json.loads(body_text))
        call_kwargs: dict[str, Any] = dict(query_params)
        if "if-match" in options:
            call_kwargs["version"] = int(options["if-match"])
        if "idempotency-key" in options:
            call_kwargs["idempotency_key"] = options["idempotency-key"]
        return self._show(lambda: operation(*call_args, **call_kwargs))

    def _match(self, method: str, path: str) -> tuple[str, tuple[str, ...]] | None:
        for route_method, route_pattern, operation_name in self._routes:
            path_match = re.fullmatch(route_pattern, path.rstrip("/") or "/")
            if route_method == method.upper() and path_match:
                return operation_name, path_match.groups()
        return None

    @staticmethod
    def _show(send: Callable[[], Response]) -> int:
        try:
            api_response = send()
        except ApiError as api_error:
            retry_note = f"  retry_after={api_error.retry_after}s" if api_error.retry_after is not None else ""
            print(f"HTTP {int(api_error.status_code)} {api_error.message}  (request_id {api_error.request_id}){retry_note}")
            return 1
        print(f"HTTP {int(api_response.status_code)}")
        if api_response.data is not None:
            print(json.dumps(api_response.data, indent=2))
        return 0


def _split_calls(arguments: list[str]) -> list[list[str]]:
    calls: list[list[str]] = [[]]
    for argument in arguments:
        if argument == "--then":
            calls.append([])
        else:
            calls[-1].append(argument)
    return calls


def main(arguments: list[str]) -> int:
    if len(arguments) < 2:
        print(__doc__)
        return 2
    logging.basicConfig(level=logging.INFO, format="  %(name)s: %(message)s")
    api_cli = ApiCli()
    exit_code = 0
    for call_arguments in _split_calls(arguments):
        options: dict[str, str] = {}
        positional: list[str] = []
        remaining = iter(call_arguments)
        for argument in remaining:
            if argument.startswith("--"):
                options[argument[2:]] = next(remaining, "")
            else:
                positional.append(argument)
        method, url, *body = positional
        print(f"\n$ {method} {url}" + (f" {body[0]}" if body else ""))
        exit_code = api_cli.call(method, url, body[0] if body else None, options) or exit_code
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
