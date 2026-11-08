import pytest

from helpers.api_test_helpers import get_site, update_site
from resources.dependencies.control_room_fake import ControlRoomClient
from resources.utils.test_data_manager import DataManager


@pytest.mark.sites
class TestApiSites:
    def test_api_renaming_a_site_then_tagging_it_keeps_both_changes(self, api_client: ControlRoomClient, data_manager: DataManager) -> None:
        leeds_depot = data_manager.get_fixed_site("Leeds Depot")
        renamed_depot = update_site(api_client, get_site(api_client, leeds_depot.mpan), {"name": "Leeds Depot North"})
        update_site(api_client, renamed_depot, {"tags": ["cold-store"]})
        stored_depot = get_site(api_client, leeds_depot.mpan)
        stored_changes = (stored_depot["name"], stored_depot["tags"])
        assert stored_changes == ("Leeds Depot North", ["cold-store"]), f"{leeds_depot.mpan} lost one of its two changes"
