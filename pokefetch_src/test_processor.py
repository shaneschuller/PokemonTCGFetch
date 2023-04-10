import pytest

from api_client import Card, Config
from file_handler import FileHandler
from processor import process_page


@pytest.fixture
def config():
    return Config()

@pytest.fixture
def file_handler(config):
    return FileHandler(config.output_directory)

def test_process_page(mocker, config, file_handler):
    cards = [
        Card(name="Card A", rarity="Common", hp=60, types=["Water"]),
        Card(name="Card B", rarity="Rare", hp=100, types=["Fire"]),
    ]

    mocker.patch('processor.FileHandler.write_cards_to_file')
    output_file = process_page(cards, config)

    assert output_file == f"{config.output_directory}/output.json"
    file_handler.write_cards_to_file.assert_called_once_with(cards, output_file)

def test_process_page_empty_cards(mocker, config, file_handler):
    mocker.patch('processor.FileHandler.write_cards_to_file')
    output_file = process_page([], config)

    assert output_file is None
    file_handler.write_cards_to_file.assert_not_called()

if __name__ == '__main__':
    pytest.main()