import os
from dotenv import load_dotenv
from prometheus_client import CollectorRegistry

load_dotenv()

import os

class Config:
    def __init__(self, api_base_url=None, max_retries=None, backoff_factor=None,
                 api_request_timeout=None, default_page_size=None):
        self.api_request_timeout = api_request_timeout or int(os.getenv("API_REQUEST_TIMEOUT", 300))
        self.prometheus_registry = CollectorRegistry()
        self.max_retries = max_retries or int(os.getenv("MAX_RETRIES", 6))
        self.backoff_factor = backoff_factor or int(os.getenv("DEFAULT_BACKOFF_FACTOR", 1))
        self.default_p_hp = os.getenv("DEFAULT_P_HP", "90 to *")
        self.default_p_rarity = os.getenv("DEFAULT_P_RARITY", "rare")
        self.default_p_type = os.getenv("DEFAULT_P_TYPE", "FIRE OR GRASS")
        self.default_page_size = int(default_page_size or os.getenv("DEFAULT_PAGE_SIZE", "100"))
        self.api_query_limit_flag = "?pageSize="
        self.api_query_flag = "&q"
        self.api_base_url = api_base_url or os.getenv("API_BASE_URL", "https://api.pokemontcg.io/v2/cards")
        self.output_directory = os.getenv("OUTPUT_DIRECTORY", "output")
        self.prometheus_port = int(os.getenv("PROMETHEUS_PORT", "8000"))

