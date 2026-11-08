import pytest

from helpers.api_test_helpers import upload_hedge
from resources.dependencies.control_room_fake import ControlRoomClient
from resources.factories.hedge import HedgeFactory


@pytest.mark.hedges
class TestApiHedges:
    def test_api_a_hedge_for_each_clock_change_day_covers_every_settlement_period(self, api_client: ControlRoomClient) -> None:
        spring_hedge = upload_hedge(api_client, HedgeFactory.build("2026-03-29"))
        autumn_hedge = upload_hedge(api_client, HedgeFactory.build("2026-10-25"))
        stored_hedges = [(hedge["delivery_date"], hedge["period_count"], hedge["total_volume_mwh"]) for hedge in (spring_hedge, autumn_hedge)]
        # 46 and 50 periods of 0.5 MWh on the days the clocks change
        assert stored_hedges == [("2026-03-29", 46, "23.000"), ("2026-10-25", 50, "25.000")], "A clock-change day was not hedged period by period"
