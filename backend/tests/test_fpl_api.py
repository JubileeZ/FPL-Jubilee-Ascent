from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import pytest
from app.clients.fpl_api import (
    fetch_bootstrap_static,
    fetch_element_gameweek_live,
    fetch_gameweek_fixtures,
    fetch_element_summary,
    fetch_user_details,
    fetch_user_team,
    fetch_entry_summary,
    fetch_entry_history,
    fetch_entry_transfers,
    fetch_gameweek_picks,
)


@pytest.mark.anyio
@patch("app.clients.fpl_api.save_raw_cache")
async def test_fetch_bootstrap_static(mock_save: MagicMock) -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {"events": [], "elements": []}
    mock_client.get.return_value = mock_response

    result = await fetch_bootstrap_static(mock_client, write_cache=True)

    assert result == {"events": [], "elements": []}
    mock_client.get.assert_called_once_with(
        "https://fantasy.premierleague.com/api/bootstrap-static/", headers=None, params=None
    )
    mock_save.assert_called_once_with("bootstrap_static.json", {"events": [], "elements": []})


@pytest.mark.anyio
@patch("app.clients.fpl_api.save_raw_cache")
async def test_fetch_element_gameweek_live(mock_save: MagicMock) -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {"elements": [{"id": 1, "stats": {}}]}
    mock_client.get.return_value = mock_response

    result = await fetch_element_gameweek_live(mock_client, gw_id=15, write_cache=True)

    assert result == {"elements": [{"id": 1, "stats": {}}]}
    mock_client.get.assert_called_once_with(
        "https://fantasy.premierleague.com/api/event/15/live/", headers=None, params=None
    )
    mock_save.assert_called_once_with("event_15_live.json", {"elements": [{"id": 1, "stats": {}}]})


@pytest.mark.anyio
@patch("app.clients.fpl_api.save_raw_cache")
async def test_fetch_gameweek_fixtures(mock_save: MagicMock) -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = [{"id": 1, "team_h": 1, "team_a": 2}]
    mock_client.get.return_value = mock_response

    result = await fetch_gameweek_fixtures(mock_client, gw_id=2, write_cache=True)

    assert result == [{"id": 1, "team_h": 1, "team_a": 2}]
    mock_client.get.assert_called_once_with(
        "https://fantasy.premierleague.com/api/fixtures/", headers=None, params={"event": 2}
    )
    mock_save.assert_called_once_with("fixtures_gw_2.json", [{"id": 1, "team_h": 1, "team_a": 2}])


@pytest.mark.anyio
@patch("app.clients.fpl_api.save_raw_cache")
async def test_fetch_element_summary(mock_save: MagicMock) -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {"fixtures": [], "history": []}
    mock_client.get.return_value = mock_response

    result = await fetch_element_summary(mock_client, player_id=301, write_cache=True)

    assert result == {"fixtures": [], "history": []}
    mock_client.get.assert_called_once_with(
        "https://fantasy.premierleague.com/api/element-summary/301/", headers=None, params=None
    )
    mock_save.assert_called_once_with("element_summary_301.json", {"fixtures": [], "history": []})


@pytest.mark.anyio
@patch("app.clients.fpl_api.save_raw_cache")
async def test_fetch_user_details(mock_save: MagicMock) -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {"player": {"id": 1234}}
    mock_client.get.return_value = mock_response

    result = await fetch_user_details(mock_client, token="fake-token", write_cache=True)

    assert result == {"player": {"id": 1234}}
    mock_client.get.assert_called_once_with(
        "https://fantasy.premierleague.com/api/me/",
        headers={"x-api-authorization": "Bearer fake-token"},
        params=None,
    )
    mock_save.assert_called_once_with("me.json", {"player": {"id": 1234}})


@pytest.mark.anyio
@patch("app.clients.fpl_api.save_raw_cache")
async def test_fetch_user_team(mock_save: MagicMock) -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {"picks": [], "transfers": []}
    mock_client.get.return_value = mock_response

    result = await fetch_user_team(mock_client, team_id=9876, token="fake-token", write_cache=True)

    assert result == {"picks": [], "transfers": []}
    mock_client.get.assert_called_once_with(
        "https://fantasy.premierleague.com/api/my-team/9876/",
        headers={"x-api-authorization": "Bearer fake-token"},
        params=None,
    )
    mock_save.assert_called_once_with("my_team_9876.json", {"picks": [], "transfers": []})


@pytest.mark.anyio
@patch("app.clients.fpl_api.save_raw_cache")
async def test_fetch_entry_summary(mock_save: MagicMock) -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {"id": 9876, "name": "FC Test"}
    mock_client.get.return_value = mock_response

    result = await fetch_entry_summary(mock_client, team_id=9876, token="fake-token", write_cache=True)

    assert result == {"id": 9876, "name": "FC Test"}
    mock_client.get.assert_called_once_with(
        "https://fantasy.premierleague.com/api/entry/9876/",
        headers={"x-api-authorization": "Bearer fake-token"},
        params=None,
    )
    mock_save.assert_called_once_with("entry_9876.json", {"id": 9876, "name": "FC Test"})


@pytest.mark.anyio
@patch("app.clients.fpl_api.save_raw_cache")
async def test_fetch_entry_history(mock_save: MagicMock) -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {"current": [], "past": []}
    mock_client.get.return_value = mock_response

    result = await fetch_entry_history(mock_client, team_id=9876, token=None, write_cache=True)

    assert result == {"current": [], "past": []}
    mock_client.get.assert_called_once_with(
        "https://fantasy.premierleague.com/api/entry/9876/history/",
        headers=None,
        params=None,
    )
    mock_save.assert_called_once_with("entry_9876_history.json", {"current": [], "past": []})


@pytest.mark.anyio
@patch("app.clients.fpl_api.save_raw_cache")
async def test_fetch_entry_transfers(mock_save: MagicMock) -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = [{"element_in": 1, "element_out": 2}]
    mock_client.get.return_value = mock_response

    result = await fetch_entry_transfers(mock_client, team_id=9876, token=None, write_cache=True)

    assert result == [{"element_in": 1, "element_out": 2}]
    mock_client.get.assert_called_once_with(
        "https://fantasy.premierleague.com/api/entry/9876/transfers/",
        headers=None,
        params=None,
    )
    mock_save.assert_called_once_with("entry_9876_transfers.json", [{"element_in": 1, "element_out": 2}])


@pytest.mark.anyio
@patch("app.clients.fpl_api.save_raw_cache")
async def test_fetch_gameweek_picks(mock_save: MagicMock) -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {"picks": []}
    mock_client.get.return_value = mock_response

    result = await fetch_gameweek_picks(mock_client, team_id=9876, gw_id=38, token=None, write_cache=True)

    assert result == {"picks": []}
    mock_client.get.assert_called_once_with(
        "https://fantasy.premierleague.com/api/entry/9876/event/38/picks/",
        headers=None,
        params=None,
    )
    mock_save.assert_called_once_with("entry_9876_picks_gw_38.json", {"picks": []})

