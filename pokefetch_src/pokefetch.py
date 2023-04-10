import os
import os
import argparse
from typing import List, Optional
from api_client import BaseApiClient, PokemonApiClient, Card
from config import Config
from processor import process_page
from slo_exporter import SloExporter
from query_helpers import parse_hp, parse_type, parse_rarity, POKEMON_TYPES, POKEMON_RARITIES
from file_handler import FileHandler


class PokeFetch:
    def __init__(self, config: Config):
        self.config = config
        self.slo_exporter = SloExporter(self.config)
        self.file_handler = FileHandler(config.output_directory)

    def run(self):
        args = self.parse_arguments()
        cards = self.fetch_cards(args)
        if not cards:
            return

        output_file = f"{self.config.output_directory}/output.json"
        self.file_handler.delete_old_output(output_file)
        self.file_handler.write_cards_to_file(cards, output_file)

        output_file = process_page(cards, self.config)
        if output_file:
            self.slo_exporter.export(output_file)



    def parse_arguments(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Fetch Pokemon TCG data based on filters.")
        parser.add_argument("-t", "--type", type=str, default=self.config.default_p_type,
                            help=f"Filter by Pokemon type. Available types: {', '.join(POKEMON_TYPES)}. "
                                 f"Use a single type (e.g., 'Fire') or multiple types separated by 'or' (e.g., 'Fire or Grass').")
        parser.add_argument("-r", "--rarity", type=str, default=self.config.default_p_rarity,
                            help=f"Filter by Pokemon rarity. Available rarities: {', '.join(POKEMON_RARITIES)}. "
                                 f"Use a single rarity (e.g., 'Common') or multiple rarities separated by 'or' (e.g., 'Common or Rare').")
        parser.add_argument("-hp", "--health", type=str, default=self.config.default_p_hp,
                            help="Filter by Pokemon HP range. Format: [min] to [max]. "
                                 "Examples: '90 to 200' (cards with HP between 90 and 200), '100 to *' (cards with HP greater than or equal to 100), "
                                 "'* to 200' (cards with HP less than or equal to 200).")
        parser.add_argument("-l", "--limit", type=int, default=self.config.default_page_size,
                            help="Limit the number of cards fetched per query.")
        return parser.parse_args()

    def fetch_cards(self, args: argparse.Namespace) -> List[Card]:
        try:
            hp_range = parse_hp(args.health)
        except ValueError as e:
            print(f"Error: {e}")
            return []

        slo_exporter = SloExporter(self.config)
        api_client: BaseApiClient = PokemonApiClient(self.config, slo_exporter)
        type_queries = parse_type(args.type)
        rarity_queries = parse_rarity(args.rarity)

        cards = [card
                 for type_query in type_queries
                 for rarity_query in rarity_queries
                 for card in api_client.fetch_cards(p_type=type_query, rarity=rarity_query, hp=hp_range,
                                                    page_size=args.limit or self.config.default_page_size)]
        return cards


def main():
    config = Config()
    pokefetch = PokeFetch(config)
    pokefetch.run()


if __name__ == "__main__":
    main()

