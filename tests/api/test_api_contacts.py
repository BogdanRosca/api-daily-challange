import pytest

from helpers.api_test_helpers import create_contact, update_contact
from resources.dependencies.control_room_fake import ControlRoomClient
from resources.enums.contact_enums import ContactRole
from resources.factories.contact import ContactFactory
from resources.utils.test_data_manager import SiteData


@pytest.mark.smoke
@pytest.mark.contacts
class TestApiContacts:
    def test_api_changing_a_contacts_email_keeps_their_other_details(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        contact = create_contact(api_client, unique_site.mpan, ContactFactory.build(role=ContactRole.BILLING))
        new_email = f"moved.{contact['email']}"
        updated_contact = update_contact(api_client, contact, {"email": new_email})
        assert updated_contact == {**contact, "email": new_email}, f"Changing the email of {contact['id']} changed other details"
