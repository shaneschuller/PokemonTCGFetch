import argparse
import pytest

from api_client import Card, Config
from file_handler import FileHandler
from pokefetch import PokeFetch
from slo_exporter import SloExporter

@pytest.fixture
def config():
    return Config()

@pytest.fixture
def slo_exporter(config):
    return SloExporter(config)

@pytest.fixture
def file_handler(config):
    return FileHandler(config.output_directory)


def test_pokefetch_run(mocker, config, slo_exporter, file_handler):
    cards = [
        Card(name="Card A", rarity="Common", hp=60, types=["Water"]),
        Card(name="Card B", rarity="Rare", hp=100, types=["Fire"]),
    ]

    mocker.patch('pokefetch.PokeFetch.parse_arguments', return_value=argparse.Namespace(type="Water", rarity="Common", health="60 to 100", limit=100))
    mocker.patch('pokefetch.PokeFetch.fetch_cards', return_value=cards)
    mocker.patch('file_handler.FileHandler.delete_old_output')
    mocker.patch('file_handler.FileHandler.write_cards_to_file')
    mocker.patch('slo_exporter.SloExporter.export')

    pokefetch = PokeFetch(config)
    pokefetch.run()

    pokefetch.file_handler.delete_old_output.assert_called_once()
    pokefetch.file_handler.write_cards_to_file.assert_called_with(cards, f"{config.output_directory}/output.json")


if __name__ == '__main__':
    pytest.main()
