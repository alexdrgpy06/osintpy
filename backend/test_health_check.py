import pytest
import httpx
import respx
from services.health_check import SystemValidator

@pytest.mark.asyncio
async def test_check_apis_all_online():
    all_targets = {**SystemValidator.CIVIC_TARGETS, **SystemValidator.GLOBAL_TARGETS}

    with respx.mock(assert_all_called=False) as respx_mock:
        for url in all_targets.values():
            respx_mock.get(url).respond(200)

        results = await SystemValidator.check_apis()

        assert len(results) == len(all_targets)
        for name in all_targets.keys():
            assert results[name] == "ONLINE ✅"

@pytest.mark.asyncio
async def test_check_apis_mixed_status():
    all_targets = list({**SystemValidator.CIVIC_TARGETS, **SystemValidator.GLOBAL_TARGETS}.items())

    if len(all_targets) < 3:
        pytest.skip("Not enough targets available to test mixed status")

    target_ok = all_targets[0]
    target_error = all_targets[1]
    target_timeout = all_targets[2]

    with respx.mock(assert_all_called=False) as respx_mock:
        # One OK
        respx_mock.get(target_ok[1]).respond(200)
        # One Error (HTTP 500)
        respx_mock.get(target_error[1]).respond(500)
        # One Timeout Exception
        respx_mock.get(target_timeout[1]).mock(side_effect=httpx.TimeoutException("Timeout"))

        # Mock the rest as OK to avoid unmocked requests
        for name, url in all_targets[3:]:
            respx_mock.get(url).respond(200)

        results = await SystemValidator.check_apis()

        assert results[target_ok[0]] == "ONLINE ✅"
        assert results[target_error[0]] == "OFFLINE ❌ (500)"
        assert results[target_timeout[0]] == "OFFLINE ❌ (TIMEOUT)"
