from http import HTTPStatus

import pytest

from helpers.api_test_helpers import request_tender, wait_for_priced_tender
from resources.dependencies.control_room_fake import ENV, ApiError, ControlRoomClient
from resources.enums.tender_enums import TenderStatus
from resources.utils.config_manager import UserCredentials
from resources.utils.test_data_manager import DataManager

@pytest.mark.tenders
class TestApiTenders:
    _buy_rate_pence_per_kwh = 24.6
    _contract_lengths_in_months = (12, 24, 36)

    def test_api_a_buy_site_tender_starts_pending_and_is_priced_at_the_buy_rate(
        self, api_client: ControlRoomClient, data_manager: DataManager
    ) -> None:
        leeds_depot = data_manager.get_fixed_site("Leeds Depot")
        pending_tender = request_tender(api_client, leeds_depot.mpan, 12)
        priced_tender = wait_for_priced_tender(api_client, pending_tender["id"])
        assert (pending_tender["status"], priced_tender["unit_rate_pence_per_kwh"]) == (TenderStatus.PENDING, self._buy_rate_pence_per_kwh)

    def test_api_a_tender_for_an_unsupported_contract_length_is_refused(
        self, api_client: ControlRoomClient, data_manager: DataManager
    ) -> None:
        leeds_depot = data_manager.get_fixed_site("Leeds Depot")
        with pytest.raises(ApiError) as refused_tender:
            api_client.request_tender(leeds_depot.mpan, {"contract_months": 18})
        assert refused_tender.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, "an 18-month tender was accepted"

    def test_api_each_contract_length_gets_its_own_priced_tender(self, api_client: ControlRoomClient, data_manager: DataManager) -> None:
        leeds_depot = data_manager.get_fixed_site("Leeds Depot")
        pending_tenders = [
            request_tender(api_client, leeds_depot.mpan, contract_months) for contract_months in self._contract_lengths_in_months
        ]
        priced_tenders = [wait_for_priced_tender(api_client, pending_tender["id"]) for pending_tender in pending_tenders]
        priced_lengths = [(priced_tender["contract_months"], priced_tender["status"]) for priced_tender in priced_tenders]
        assert priced_lengths == [(contract_months, TenderStatus.PRICED) for contract_months in self._contract_lengths_in_months]
        assert len({priced_tender["id"] for priced_tender in priced_tenders}) == len(self._contract_lengths_in_months), (
            "two lengths shared one tender"
        )

    def test_api_a_priced_tender_keeps_its_rate_when_read_again(self, api_client: ControlRoomClient, data_manager: DataManager) -> None:
        leeds_depot = data_manager.get_fixed_site("Leeds Depot")
        pending_tender = request_tender(api_client, leeds_depot.mpan, 36)
        priced_tender = wait_for_priced_tender(api_client, pending_tender["id"])
        reread_rates = [api_client.get_tender(pending_tender["id"]).data["unit_rate_pence_per_kwh"] for _ in range(6)]
        assert reread_rates == [priced_tender["unit_rate_pence_per_kwh"]] * 6, f"{pending_tender['id']} changed its rate after it was priced"
