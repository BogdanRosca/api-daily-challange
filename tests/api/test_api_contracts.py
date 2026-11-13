from datetime import date, timedelta

import pytest

from helpers.api_test_helpers import create_contract, list_site_contracts
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

    def test_api_a_sites_fixed_contracts_are_listed_oldest_first_across_pages(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        contract_types_by_month = {
            "2027-01": ContractType.FIXED,
            "2027-02": ContractType.FLEX,
            "2027-03": ContractType.FIXED,
            "2027-04": ContractType.FIXED,
            "2027-05": ContractType.FLEX,
            "2027-06": ContractType.FIXED,
            "2027-07": ContractType.FIXED,
        }
        for month, contract_type in contract_types_by_month.items():
            last_day = (date.fromisoformat(f"{month}-01") + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            create_contract(api_client, unique_site.mpan, ContractFactory.build(f"{month}-01", last_day.isoformat(), contract_type))
        fixed_start_dates = [fixed_contract["start_date"] for fixed_contract in list_site_contracts(api_client, unique_site.mpan, ContractType.FIXED)]
        expected_start_dates = [f"{month}-01" for month, contract_type in contract_types_by_month.items() if contract_type == ContractType.FIXED]
        assert fixed_start_dates == expected_start_dates, f"{unique_site.mpan} did not list exactly its FIXED contracts, oldest first"
