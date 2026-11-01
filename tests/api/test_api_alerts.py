import pytest

from helpers.api_test_helpers import create_alert_rule, evaluate_day, list_site_alerts
from resources.dependencies.control_room_fake import ControlRoomClient
from resources.factories.alert_rule import AlertRuleFactory
from resources.utils.test_data_manager import SiteData


@pytest.mark.alerts
class TestApiAlerts:
    def test_api_a_week_of_consumption_alerts_only_on_days_above_the_threshold(self, api_client: ControlRoomClient, unique_site: SiteData) -> None:
        alert_rule = create_alert_rule(api_client, unique_site.mpan, AlertRuleFactory.build(threshold_kwh="100.000"))
        daily_kwh = {
            "2026-11-01": "80.000",
            "2026-11-02": "100.000",
            "2026-11-03": "100.001",
            "2026-11-04": "120.500",
            "2026-11-05": "99.999",
            "2026-11-06": "150.000",
            "2026-11-07": "60.000",
            "2026-11-08": "101.000",
        }
        for day, kwh in daily_kwh.items():
            evaluate_day(api_client, unique_site.mpan, day, kwh)
        alerted_days = [site_alert["day"] for site_alert in list_site_alerts(api_client, unique_site.mpan)]
        assert alerted_days == ["2026-11-03", "2026-11-04", "2026-11-06", "2026-11-08"], f"Rule {alert_rule['id']} alerted on the wrong days"
