from http import HTTPStatus

import pytest

from helpers.api_test_helpers import list_site_meters, register_meter, submit_meter_reading
from resources.dependencies.control_room_fake import ApiError, ControlRoomClient
from resources.factories.meter import MeterFactory
from resources.utils.test_data_manager import SiteData


@pytest.mark.meters
class TestApiMeters:
    def test_api_a_sites_meters_are_listed_in_registration_order_across_pages(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        meters_to_register = 7
        meter_payloads = [MeterFactory.build() for _ in range(meters_to_register)]
        registered_serials = [register_meter(api_client, unique_site.mpan, meter_payload)["serial_number"] for meter_payload in meter_payloads]
        listed_serials = [site_meter["serial_number"] for site_meter in list_site_meters(api_client, unique_site.mpan)]
        assert listed_serials == registered_serials

    def test_api_a_meter_register_may_stay_level_but_a_reading_may_not_repeat_a_date(
        self, api_client: ControlRoomClient, unique_site: SiteData
    ) -> None:
        meter = register_meter(api_client, unique_site.mpan, MeterFactory.build())
        submit_meter_reading(api_client, meter["id"], "2026-11-01", "100.000")
        submit_meter_reading(api_client, meter["id"], "2026-11-02", "100.000")
        with pytest.raises(ApiError) as repeated_date_error:
            api_client.submit_reading(meter["id"], {"read_at": "2026-11-02", "register_kwh": "120.000"})
        assert repeated_date_error.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        stored_readings = api_client.list_readings(meter["id"]).data["items"]
        assert [(stored["read_at"], stored["register_kwh"]) for stored in stored_readings] == [("2026-11-01", "100.000"), ("2026-11-02", "100.000")]
