# processor.py

import os
from typing import List, Optional

from api_client import Card
from config import Config
from file_handler import FileHandler
import json


def process_page(cards: List[Card], config: Config) -> Optional[str]:
    if not cards:
        # Log the empty page
        print("Empty page encountered.")
        return None

    file_handler = FileHandler(config.output_directory)
    output_file = f"{config.output_directory}/output.json"
    file_handler.write_cards_to_file(cards, output_file)

    return output_file

