import requests
from abc import ABC, abstractmethod
from typing import List, Optional
from config import Config
import urllib.parse
import time
from dataclasses import dataclass, field
from slo_exporter import SloExporter

@dataclass
class Card:
    name: str
    rarity: Optional[str] = None
    hp: Optional[int] = None
    types: List[str] = field(default_factory=list)

    def _asdict(self):
        return self.__dict__


class BaseApiClient(ABC):

    @abstractmethod
    def fetch_cards(self, p_type: Optional[str] = None, rarity: Optional[str] = None, hp: Optional[int] = None,
                    page_size: int = 100) -> List[Card]:
        pass

class PokemonApiClient(BaseApiClient):
    def __init__(self, config: Config, slo_exporter: SloExporter):
        self.config = config
        self.slo_exporter = slo_exporter

    def fetch_cards(self, p_type: Optional[str] = None, rarity: Optional[str] = None, hp: Optional[int] = None,
                    page_size: int = 100) -> List[Card]:

        max_retries = self.config.max_retries
        backoff_factor = self.config.backoff_factor

        query_params = []
        if p_type:
            query_params.append(f"types:{p_type}")
        if rarity:
            query_params.append(f'rarity:"{rarity}"')
        if hp:
            query_params.append(f"hp:{urllib.parse.quote(str(hp))}")
        query = "%20".join(query_params)
        page_size = max(page_size or self.config.default_page_size, 1)
        url = f"{self.config.api_base_url}?pageSize={page_size}&q={query}"

        print(f"p_type:{p_type} | rarity:{rarity} | hp:{hp} | page_size:{page_size}")

        for retries in range(max_retries):
            try:
                start_time = time.time()
                response = requests.get(url, timeout=self.config.api_request_timeout)
                self.slo_exporter.request_succeeded(start_time)
                print(response.url)
                response.raise_for_status()

                data = response.json()
                cards_data = data.get('data', [])

                cards = [
                    Card(
                        name=card_data.get('name'),
                        rarity=card_data.get('rarity'),
                        hp=int(card_data.get('hp')) if card_data.get('hp') else None,
                        types=card_data.get('types', [])
                    )
                    for card_data in cards_data
                ]

                return cards

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and retries < max_retries - 1:
                    sleep_duration = backoff_factor ** retries
                    self.slo_exporter.update_backoff_metrics(backoff_factor, sleep_duration)
                    print(f"PokemonTCG Servers are overwhelmed, slowing down for {sleep_duration} seconds.")
                    time.sleep(sleep_duration)
                    print(f"It has been {sleep_duration} seconds, continuing to process.")
                else:
                    print(f"Error {e.response.status_code}: {e.response.reason}. Unable to fetch cards.")
                    self.slo_exporter.request_failed()
                    return []
            except requests.exceptions.Timeout:
                print(f"Error: Request timed out.")
                self.slo_exporter.request_timed_out()
                return []
