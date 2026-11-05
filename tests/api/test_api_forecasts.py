import pytest

from helpers.api_test_helpers import list_forecast_days, upload_forecast, wait_for_forecast_upload
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
