# file_handler.py
import os
import json
from typing import List
from api_client import Card

class FileHandler:

    def __init__(self, output_directory: str):
        self.output_directory = output_directory

    def create_directory(self):
        os.makedirs(self.output_directory, exist_ok=True)


    def delete_old_output(self, output_file: str):
        if os.path.exists(output_file):
            os.remove(output_file)

    def write_cards_to_file(self, cards: List[Card], output_file: str):
        self.create_directory()

        data = {
            "Cards": [
                {
                    "Name": card.name,
                    "Type": card.types,
                    "HP": card.hp,
                    "Rarity": card.rarity
                } for card in cards
            ]
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)
