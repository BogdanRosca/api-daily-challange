import pytest

from helpers.api_test_helpers import create_contract
from resources.dependencies.control_room_fake import ApiError, ControlRoomClient
from resources.enums.contract_enums import ContractType
from resources.enums.site_enums import SiteType
from resources.factories.contract import ContractFactory
from resources.utils.test_data_manager import SiteData


# SELL sites keep the BUY sites of the tests after these in the pool where they were
@pytest.mark.contracts
@pytest.mark.parametrize("site_type", [SiteType.SELL], indirect=True)
class TestApiContracts:
    @pytest.mark.usefixtures("overlaps_allowed")
    def test_api_overlapping_contracts_are_both_stored_when_overlaps_are_allowed(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        first_contract = create_contract(api_client, unique_site.mpan, ContractFactory.build("2026-11-01", "2026-11-30"))
        second_contract = create_contract(api_client, unique_site.mpan, ContractFactory.build("2026-11-15", "2026-12-15"))
        listed_ids = [listed_contract["id"] for listed_contract in api_client.list_contracts(unique_site.mpan).data["items"]]
        assert listed_ids == [first_contract["id"], second_contract["id"]], f"{unique_site.mpan} did not keep both contracts"

    def test_api_a_contract_sharing_one_day_with_an_existing_contract_is_rejected(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        create_contract(api_client, unique_site.mpan, ContractFactory.build("2026-11-01", "2026-11-30"))
        with pytest.raises(ApiError) as overlap_error:
            api_client.create_contract(unique_site.mpan, ContractFactory.build("2026-11-30", "2026-12-31"))
        assert overlap_error.value.status_code == 409, f"{unique_site.mpan} accepted a contract sharing 2026-11-30"
        assert [listed_contract["start_date"] for listed_contract in api_client.list_contracts(unique_site.mpan).data["items"]] == ["2026-11-01"]

    def test_api_back_to_back_contracts_either_side_of_the_spring_clock_change_keep_their_uk_dates(
        self, api_client: ControlRoomClient, unique_site: SiteData
    ) -> None:
        create_contract(api_client, unique_site.mpan, ContractFactory.build("2027-03-01", "2027-03-31"))
        create_contract(api_client, unique_site.mpan, ContractFactory.build("2027-04-01", "2027-04-30", ContractType.FLEX))
        listed_contracts = api_client.list_contracts(unique_site.mpan).data["items"]
        stored_dates = [(listed_contract["start_date"], listed_contract["end_date"]) for listed_contract in listed_contracts]
        expected_dates = [("2027-03-01", "2027-03-31"), ("2027-04-01", "2027-04-30")]
        assert stored_dates == expected_dates, f"{unique_site.mpan} did not store March and April as UK dates"
