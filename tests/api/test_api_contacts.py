import pytest

from helpers.api_test_helpers import create_contact, hand_over_primary_contact, list_site_contacts, update_contact
from resources.dependencies.control_room_fake import ControlRoomClient
from resources.enums.contact_enums import ContactRole
from resources.factories.contact import ContactFactory
from resources.utils.test_data_manager import SiteData


@pytest.mark.smoke
@pytest.mark.contacts
class TestApiContacts:
    _handovers = 3

    def test_api_changing_a_contacts_email_keeps_their_other_details(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        contact = create_contact(api_client, unique_site.mpan, ContactFactory.build(role=ContactRole.BILLING))
        new_email = f"moved.{contact['email']}"
        updated_contact = update_contact(api_client, contact, {"email": new_email})
        assert updated_contact == {**contact, "email": new_email}, f"Changing the email of {contact['id']} changed other details"

    def test_api_each_primary_contact_handover_leaves_only_the_new_primary(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        create_contact(api_client, unique_site.mpan, ContactFactory.build(role=ContactRole.PRIMARY))
        billing_contact = create_contact(api_client, unique_site.mpan, ContactFactory.build(role=ContactRole.BILLING))
        for _ in range(self._handovers):
            new_primary = hand_over_primary_contact(api_client, unique_site.mpan, ContactFactory.build(role=ContactRole.PRIMARY))
            contact_roles = {site_contact["id"]: site_contact["role"] for site_contact in list_site_contacts(api_client, unique_site.mpan)}
            assert contact_roles == {new_primary["id"]: ContactRole.PRIMARY, billing_contact["id"]: ContactRole.BILLING}, (
                f"Handing {unique_site.mpan} over to {new_primary['id']} did not leave it as the only PRIMARY"
            )
