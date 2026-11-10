import pytest

from helpers.api_test_helpers import create_area, get_site, list_site_areas, update_site
from resources.dependencies.control_room_fake import ControlRoomClient
from resources.enums.site_enums import SiteType
from resources.factories.area import AreaFactory
from resources.utils.test_data_manager import DataManager, SiteData


@pytest.mark.sites
class TestApiSites:
    def test_api_renaming_a_site_then_tagging_it_keeps_both_changes(self, api_client: ControlRoomClient, data_manager: DataManager) -> None:
        leeds_depot = data_manager.get_fixed_site("Leeds Depot")
        renamed_depot = update_site(api_client, get_site(api_client, leeds_depot.mpan), {"name": "Leeds Depot North"})
        update_site(api_client, renamed_depot, {"tags": ["cold-store"]})
        stored_depot = get_site(api_client, leeds_depot.mpan)
        stored_changes = (stored_depot["name"], stored_depot["tags"])
        assert stored_changes == ("Leeds Depot North", ["cold-store"]), f"{leeds_depot.mpan} lost one of its two changes"

    @pytest.mark.parametrize("site_type", [SiteType.SELL], indirect=True)
    def test_api_a_sites_areas_are_listed_a_to_z_ignoring_case(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        area_names = ["boiler room", "Cold store", "Annexe", "annexe", "Boiler room"]
        created_areas = [create_area(api_client, unique_site.mpan, AreaFactory.build(area_name)) for area_name in area_names]
        expected_area_ids = [area["id"] for area in sorted(created_areas, key=lambda area: area["name"].lower())]
        listed_area_ids = [area["id"] for area in list_site_areas(api_client, unique_site.mpan)]
        assert listed_area_ids == expected_area_ids, f"{unique_site.mpan} listed its areas out of order"
