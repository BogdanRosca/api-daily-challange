import pytest

from helpers.api_test_helpers import bill_month, list_site_invoices
from resources.dependencies.control_room_fake import ControlRoomClient
from resources.utils.test_data_manager import SiteData


@pytest.mark.invoices
class TestApiInvoices:
    def test_api_two_billed_months_give_two_invoices_with_rounded_amounts(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        bill_month(api_client, unique_site.mpan, "2026-10", "100.500", "10.5")
        bill_month(api_client, unique_site.mpan, "2026-11", "0.500", "3")
        site_invoices = list_site_invoices(api_client, unique_site.mpan)
        billed_amounts = [(site_invoice["billing_month"], site_invoice["amount_pence"]) for site_invoice in site_invoices]
        assert billed_amounts == [("2026-10", 1055), ("2026-11", 2)], f"{unique_site.mpan} was not billed exactly once per month"
