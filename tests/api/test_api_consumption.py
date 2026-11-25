import calendar
from datetime import date
from decimal import Decimal

import pytest

from helpers.api_test_helpers import get_consumption_summary, list_consumption_days, list_month_consumption_days, submit_daily_reads
from resources.dependencies.control_room_fake import ControlRoomClient
from resources.utils.test_data_manager import SiteData


@pytest.mark.consumption
class TestApiConsumption:
    _outside_month_kwh = "99.000"
    _weekday_kwh = "42.500"
    _weekend_kwh = "8.250"
    _peak_kwh = "95.000"

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

    def test_api_a_sites_monthly_summary_names_its_busiest_day_the_earliest_on_a_tie(
        self, api_client: ControlRoomClient, unique_site: SiteData
    ) -> None:
        month_kwh = self._working_week_and_weekend_reads("2026-11")
        month_kwh.update(dict.fromkeys(("2026-11-07", "2026-11-19"), self._peak_kwh))
        submit_daily_reads(api_client, unique_site.mpan, month_kwh)
        consumption_summary = get_consumption_summary(api_client, unique_site.mpan, "2026-11")
        expected_peak = (self._busiest_day(month_kwh), self._peak_kwh)
        assert (consumption_summary["peak_day"], consumption_summary["peak_kwh"]) == expected_peak, (
            f"The November summary of {unique_site.mpan} named {consumption_summary['peak_day']} as its busiest day, not {expected_peak[0]}"
        )

    @classmethod
    def _working_week_and_weekend_reads(cls, consumption_month: str) -> dict[str, str]:
        """A site that works Monday to Friday and ticks over at weekends."""
        year, month_number = (int(month_part) for month_part in consumption_month.split("-"))
        month_days = [date(year, month_number, day_number) for day_number in range(1, calendar.monthrange(year, month_number)[1] + 1)]
        weekday_reads = {month_day.isoformat(): cls._weekday_kwh for month_day in month_days if month_day.weekday() < 5}
        weekend_reads = {month_day.isoformat(): cls._weekend_kwh for month_day in month_days if month_day.weekday() >= 5}
        return {**weekday_reads, **weekend_reads}

    @staticmethod
    def _busiest_day(kwh_by_day: dict[str, str]) -> str:
        """The day with the most kWh. max() keeps the first of equal days, which is the contract's earliest on a tie."""
        return max(kwh_by_day, key=lambda day: Decimal(kwh_by_day[day]))

    @staticmethod
    def _reads_for_every_day_of(consumption_month: str) -> dict[str, str]:
        """One read a day, rising through the month, so the last day is the busiest."""
        year, month_number = (int(month_part) for month_part in consumption_month.split("-"))
        days_in_month = calendar.monthrange(year, month_number)[1]
        return {
            f"{consumption_month}-{day_number:02d}": f"{Decimal('10.125') + Decimal('1.5') * day_number:.3f}"
            for day_number in range(1, days_in_month + 1)
        }
