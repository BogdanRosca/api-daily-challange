import pytest

from helpers.api_test_helpers import upload_hedge
from resources.dependencies.control_room_fake import ControlRoomClient
from resources.factories.hedge import HedgeFactory


@pytest.mark.hedges
class TestApiHedges:
    _traded_day_volume_mwh = "12.000"

    def test_api_a_hedge_for_each_clock_change_day_covers_every_settlement_period(self, api_client: ControlRoomClient) -> None:
        spring_hedge = upload_hedge(api_client, HedgeFactory.build("2026-03-29"))
        autumn_hedge = upload_hedge(api_client, HedgeFactory.build("2026-10-25"))
        stored_hedges = [(hedge["delivery_date"], hedge["period_count"], hedge["total_volume_mwh"]) for hedge in (spring_hedge, autumn_hedge)]
        # 46 and 50 periods of 0.5 MWh on the days the clocks change
        assert stored_hedges == [("2026-03-29", 46, "23.000"), ("2026-10-25", 50, "25.000")], "A clock-change day was not hedged period by period"

    @pytest.mark.parametrize(
        "delivery_date",
        ["2026-11-20", "2026-03-29", "2026-10-25"],
        ids=["ordinary_day", "spring_clock_change", "autumn_clock_change"],
    )
    def test_api_a_hedge_for_a_days_trade_covers_exactly_the_traded_volume(self, api_client: ControlRoomClient, delivery_date: str) -> None:
        stored_hedge = upload_hedge(api_client, HedgeFactory.build_for_day_volume(delivery_date, self._traded_day_volume_mwh))
        assert stored_hedge["total_volume_mwh"] == self._traded_day_volume_mwh, (
            f"{delivery_date} hedged {stored_hedge['total_volume_mwh']} MWh over {stored_hedge['period_count']} periods, "
            f"but {self._traded_day_volume_mwh} MWh was traded"
        )
