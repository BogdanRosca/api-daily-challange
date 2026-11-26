from decimal import ROUND_HALF_UP, Decimal

import pytest

from helpers.api_test_helpers import bill_month, get_consumption_summary, list_site_invoices, submit_daily_reads
from resources.dependencies.control_room_fake import ControlRoomClient
from resources.enums.site_enums import SiteType
from resources.factories.daily_read import DailyReadFactory
from resources.utils.test_data_manager import SiteData
from datetime import date

@pytest.mark.invoices
class TestApiInvoices:
    _unit_rate_pence_per_kwh = "24.6"
    _fortnight = 14
    _start_date = date.fromisoformat("2026-11-01")

    def test_api_two_billed_months_give_two_invoices_with_rounded_amounts(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        bill_month(api_client, unique_site.mpan, "2026-10", "100.500", "10.5")
        bill_month(api_client, unique_site.mpan, "2026-11", "0.500", "3")
        site_invoices = list_site_invoices(api_client, unique_site.mpan)
        billed_amounts = [(site_invoice["billing_month"], site_invoice["amount_pence"]) for site_invoice in site_invoices]
        assert billed_amounts == [("2026-10", 1055), ("2026-11", 2)], f"{unique_site.mpan} was not billed exactly once per month"

    @pytest.mark.parametrize("site_type", [SiteType.BUY, SiteType.SELL], ids=["BUY", "SELL"], indirect=True)
    def test_api_every_billed_month_is_charged_in_whole_pence(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        billed_usage = {"2026-09": ("100.500", "10.5"), "2026-10": ("0.500", "5"), "2026-11": ("12.345", "24.6")}
        for billing_month, (consumption_kwh, unit_rate) in billed_usage.items():
            bill_month(api_client, unique_site.mpan, billing_month, consumption_kwh, unit_rate)
        site_invoices = list_site_invoices(api_client, unique_site.mpan)
        billed_amounts = {site_invoice["billing_month"]: site_invoice["amount_pence"] for site_invoice in site_invoices}
        expected_amounts = {
            billing_month: self._billed_pence(consumption_kwh, unit_rate, unique_site.site_type)
            for billing_month, (consumption_kwh, unit_rate) in billed_usage.items()
        }
        assert billed_amounts == expected_amounts, f"{unique_site.mpan} ({unique_site.site_type}) was not billed in whole pence"

    def test_api_a_month_is_billed_for_every_kwh_read_in_it(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        fortnight_kwh = DailyReadFactory.build(self._fortnight, first_day=self._start_date)
        billing_month = min(fortnight_kwh)[:7]
        submit_daily_reads(api_client, unique_site.mpan, fortnight_kwh)
        month_summary = get_consumption_summary(api_client, unique_site.mpan, billing_month)
        month_invoice = bill_month(api_client, unique_site.mpan, billing_month, month_summary["total_kwh"], self._unit_rate_pence_per_kwh)
        read_kwh = sum(map(Decimal, fortnight_kwh.values()))
        expected_pence = self._billed_pence(f"{read_kwh}", self._unit_rate_pence_per_kwh, unique_site.site_type)
        assert month_invoice["amount_pence"] == expected_pence, (
            f"{unique_site.mpan} was billed {month_invoice['amount_pence']}p for {billing_month}, not {expected_pence}p for its {read_kwh} kWh"
        )

    @staticmethod
    def _billed_pence(consumption_kwh: str, unit_rate: str, site_type: SiteType) -> int:
        """What billing charges for a month: kWh x rate, rounded half up to whole pence, negative (a credit) for a SELL site."""
        signed_pence = Decimal(consumption_kwh) * Decimal(unit_rate) * (-1 if site_type == SiteType.SELL else 1)
        return int(signed_pence.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
