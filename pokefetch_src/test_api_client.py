import json

import pytest
from unittest.mock import MagicMock

from requests import Response, Timeout

from api_client import PokemonApiClient, BaseApiClient, Card, Config
from slo_exporter import SloExporter


@pytest.fixture
def config():
    return Config(
        api_base_url="https://api.pokemontcg.io/v2/cards",
        max_retries=3,
        backoff_factor=2,
        api_request_timeout=5,
        default_page_size=100,
    )


@pytest.fixture
def slo_exporter(config):
    return SloExporter(config)


def test_base_api_client():
    with pytest.raises(TypeError):
        BaseApiClient()


def test_fetch_cards(mocker, config, slo_exporter):
    cards_data = [
        {
            "name": "Card P",
            "rarity": "Common",
            "hp": "60",
            "types": ["Electric"]
        },
        {
            "name": "Card B",
            "rarity": "Common",
            "hp": "40",
            "types": ["Grass"]
        }
    ]

    api_response = {
        "data": cards_data
    }

    mocked_response = Response()
    mocked_response.status_code = 200
    mocked_response._content = json.dumps(api_response).encode('utf-8')

    mocker.patch('requests.get', return_value=mocked_response)

    client = PokemonApiClient(config, slo_exporter)
    cards = client.fetch_cards()

    assert len(cards) == 2
    assert cards[0] == Card(name="Card P", rarity="Common", hp=60, types=["Electric"])
    assert cards[1] == Card(name="Card B", rarity="Common", hp=40, types=["Grass"])


def test_fetch_cards_with_query_parameters(mocker, config, slo_exporter):
    cards_data = [
        {
            "name": "Card C",
            "rarity": "Rare Holo",
            "hp": "120",
            "types": ["Fire"]
        }
    ]

    api_response = {
        "data": cards_data
    }

    mocked_response = Response()
    mocked_response.status_code = 200
    mocked_response._content = json.dumps(api_response).encode('utf-8')

    mocker.patch('requests.get', return_value=mocked_response)

    client = PokemonApiClient(config, slo_exporter)
    cards = client.fetch_cards(p_type="Fire", rarity="Rare Holo")

    assert len(cards) == 1
    assert cards[0] == Card(name="Card C", rarity="Rare Holo", hp=120, types=["Fire"])


def test_fetch_cards_with_request_timeout(mocker, config, slo_exporter):
    mocker.patch('requests.get', side_effect=Timeout)

    client = PokemonApiClient(config, slo_exporter)
    slo_exporter.request_timed_out = MagicMock()
    cards = client.fetch_cards()

    assert len(cards) == 0
    slo_exporter.request_timed_out.assert_called_once()


def test_fetch_cards_with_http_error(mocker, config, slo_exporter):
    mocked_response = Response()
    mocked_response.status_code = 500

    mocker.patch('requests.get', return_value=mocked_response)

    client = PokemonApiClient(config, slo_exporter)
    slo_exporter.request_failed = MagicMock()
    cards = client.fetch_cards()

    assert len(cards) == 0
    slo_exporter.request_failed.assert_called_once()


if __name__ == "__main__":
    pytest.main()
