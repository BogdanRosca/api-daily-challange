import calendar
from decimal import Decimal

import pytest

from helpers.api_test_helpers import get_consumption_summary, list_consumption_days, list_month_consumption_days, submit_daily_reads
from resources.dependencies.control_room_fake import ControlRoomClient
from resources.utils.test_data_manager import SiteData


@pytest.mark.consumption
class TestApiConsumption:
    _outside_month_kwh = "99.000"

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

    @pytest.mark.parametrize(
        ("consumption_month", "day_before", "day_after"),
        [("2026-11", "2026-10-31", "2026-12-01"), ("2026-12", "2026-11-30", "2027-01-01")],
        ids=["November", "December"],
    )
    def test_api_a_sites_daily_consumption_for_a_month_matches_its_monthly_summary(
        self, api_client: ControlRoomClient, unique_site: SiteData, consumption_month: str, day_before: str, day_after: str
    ) -> None:
        month_kwh = self._reads_for_every_day_of(consumption_month)
        submit_daily_reads(api_client, unique_site.mpan, {**month_kwh, day_before: self._outside_month_kwh, day_after: self._outside_month_kwh})
        expected_month = (len(month_kwh), sum(map(Decimal, month_kwh.values())))
        consumption_summary = get_consumption_summary(api_client, unique_site.mpan, consumption_month)
        assert (consumption_summary["days_with_reads"], Decimal(consumption_summary["total_kwh"])) == expected_month, (
            f"The {consumption_month} summary of {unique_site.mpan} does not add up its own days"
        )
        month_days = list_month_consumption_days(api_client, unique_site.mpan, consumption_month)
        listed_total = sum((Decimal(consumption_day["kwh"]) for consumption_day in month_days), Decimal(0))
        assert (len(month_days), listed_total) == expected_month, (
            f"The daily consumption of {unique_site.mpan} in {consumption_month} does not match its monthly summary"
        )

    @staticmethod
    def _reads_for_every_day_of(consumption_month: str) -> dict[str, str]:
        """One read a day, rising through the month, so the last day is the busiest."""
        year, month_number = (int(month_part) for month_part in consumption_month.split("-"))
        days_in_month = calendar.monthrange(year, month_number)[1]
        return {
            f"{consumption_month}-{day_number:02d}": f"{Decimal('10.125') + Decimal('1.5') * day_number:.3f}"
            for day_number in range(1, days_in_month + 1)
        }
