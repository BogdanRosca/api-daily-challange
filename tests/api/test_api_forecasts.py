import pytest

from helpers.api_test_helpers import list_forecast_days, revise_forecast, upload_forecast, wait_for_forecast_upload
from resources.dependencies.control_room_fake import ControlRoomClient
from resources.factories.forecast import ForecastFactory
from resources.utils.test_data_manager import SiteData


@pytest.mark.forecasts
class TestApiForecasts:
    def test_api_a_processed_two_day_forecast_stores_both_days_with_their_totals(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        forecast_payload = ForecastFactory.build(["2026-11-10", "2026-11-11"])
        upload_id = upload_forecast(api_client, unique_site.mpan, forecast_payload)
        processed_upload = wait_for_forecast_upload(api_client, upload_id)
        forecast_days = list_forecast_days(api_client, unique_site.mpan)
        stored_days = [(forecast_day["day"], forecast_day["period_count"], forecast_day["total_kwh"]) for forecast_day in forecast_days]
        # periods 1 to 48 at 0.1 kWh a step add up to 0.1 x 1176 = 117.6 kWh a day
        assert (processed_upload["row_count"], stored_days) == (96, [("2026-11-10", 48, "117.600"), ("2026-11-11", 48, "117.600")]), (
            f"{unique_site.mpan} did not store both forecast days"
        )

    def test_api_a_revised_forecast_replaces_only_the_days_it_contains(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        first_upload_id = upload_forecast(api_client, unique_site.mpan, ForecastFactory.build(["2026-11-17", "2026-11-18"]))
        wait_for_forecast_upload(api_client, first_upload_id)
        revised_forecast = revise_forecast(api_client, unique_site.mpan, ForecastFactory.build(["2026-11-18"], kwh_step=0.2))
        stored_days = [(forecast_day["day"], forecast_day["period_count"], forecast_day["total_kwh"]) for forecast_day in revised_forecast]
        # 0.1 kWh a step adds up to 117.6 kWh a day and 0.2 kWh a step to 235.2: only the revised 18th doubles
        assert stored_days == [("2026-11-17", 48, "117.600"), ("2026-11-18", 48, "235.200")], (
            f"{unique_site.mpan} does not show the revised 18 November next to the unrevised 17th"
        )
