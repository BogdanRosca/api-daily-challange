"""Stands in for the factory-boy ContactFactory. In the real repo: resources/factories/control_room/contact.py."""

from __future__ import annotations

import uuid
from typing import Any

from resources.enums.contact_enums import ContactRole


class ContactFactory:
    """Builds a site contact nobody else uses: a unique name and email, a UK mobile number and a role."""

    @classmethod
    def build(cls, role: ContactRole = ContactRole.PRIMARY) -> dict[str, Any]:
        contact_suffix = uuid.uuid4().hex[:8]
        return {
            "name": f"QA Contact {contact_suffix}",
            "email": f"qa.contact.{contact_suffix}@example.com",
            "role": role.value,
            "phone": f"+4477009{int(contact_suffix, 16) % 100000:05d}",
        }
