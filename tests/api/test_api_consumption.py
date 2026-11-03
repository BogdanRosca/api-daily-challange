from decimal import Decimal

import pytest

from helpers.api_test_helpers import list_consumption_days, submit_daily_reads
from resources.dependencies.control_room_fake import ControlRoomClient
from resources.utils.test_data_manager import SiteData


@pytest.mark.consumption
class TestApiConsumption:
    def test_api_a_sites_weekly_consumption_adds_up_the_days_in_the_week_only(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        week_kwh = {
            "2026-11-02": "10.500",
            "2026-11-03": "20.250",
            "2026-11-04": "0.000",
            "2026-11-05": "31.125",
            "2026-11-06": "18.000",
            "2026-11-07": "7.625",
            "2026-11-08": "12.500",
        }
        submit_daily_reads(api_client, unique_site.mpan, {**week_kwh, "2026-11-01": "99.000", "2026-11-09": "99.000"})
        weekly_days = list_consumption_days(api_client, "2026-11-02", "2026-11-09", unique_site.mpan)
        weekly_total = sum((Decimal(consumption_day["kwh"]) for consumption_day in weekly_days), Decimal(0))
        assert weekly_total == sum(map(Decimal, week_kwh.values())), f"The week of {unique_site.mpan} did not add up to its own seven days"
