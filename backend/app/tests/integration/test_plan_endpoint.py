import asyncio

from backend.app.api.routes_plan import ConstraintInput, PlanRequest, PreferenceInput, compute_plan


def test_compute_plan_returns_blocks() -> None:
    request = PlanRequest(
        year=2024,
        country="CA",
        region="ON",
        timezone="America/Toronto",
        pto_total=15,
        blocks_max=3,
        weekend=["SAT", "SUN"],
        goal="max_total",
        prefs=PreferenceInput(reserve_pto=3, season_spread=True),
        constraints=ConstraintInput(min_block_len=3, max_block_len=14),
    )
    response = asyncio.run(compute_plan(request))
    assert "plans" in response.model_dump()
    if response.plans:
        assert response.plans[0].blocks
