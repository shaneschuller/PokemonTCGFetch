import time

from prometheus_client import start_http_server, Counter, Gauge, Histogram

from config import Config


class SloExporter:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Config):
        if self._initialized:
            return

        self.config = config
        registry = self.config.prometheus_registry
        if "pokemon_cards_output" not in registry._names_to_collectors:
            self.output_counter = Counter("pokemon_cards_output", "Number of Pokemon cards output to a file")
        if "pokemon_failed_requests" not in registry._names_to_collectors:
            self.failed_request_counter = Counter("pokemon_failed_requests", "Number of failed requests to the Pokemon API")
        if "pokemon_total_requests" not in registry._names_to_collectors:
            self.total_request_counter = Counter("pokemon_total_requests", "Number of total requests to the Pokemon API")
        if "pokemon_request_latency" not in registry._names_to_collectors:
            self.latency_histogram = Histogram("pokemon_request_latency", "Latency of requests to the Pokemon API")
        if "pokemon_request_timeout" not in registry._names_to_collectors:
            self.timeout_counter = Counter("pokemon_request_timeout",
                                           "Number of requests to the Pokemon API that timed out")
        if "backoff_factor" not in registry._names_to_collectors:
            self.backoff_factor_gauge = Gauge("backoff_factor", "Current backoff factor for rate limiting")
        if "sleep_duration" not in registry._names_to_collectors:
            self.sleep_duration_gauge = Gauge("sleep_duration", "Current sleep duration for rate limiting")

        self._initialized = True

    def update_backoff_metrics(self, backoff_factor: int, sleep_duration: int):
        self.backoff_factor_gauge.set(backoff_factor)
        self.sleep_duration_gauge.set(sleep_duration)

    def export(self, output_file: str):
        num_cards = sum(1 for _ in open(output_file))
        self.output_counter.inc(num_cards)
        start_http_server(self.config.prometheus_port)

    def request_succeeded(self, start_time: float):
        self.total_request_counter.inc()
        elapsed_time = time.time() - start_time
        self.latency_histogram.observe(elapsed_time)

    def request_failed(self):
        self.total_request_counter.inc()
        self.failed_request_counter.inc()

    def request_timed_out(self):
        self.total_request_counter.inc()
        self.timeout_counter.inc()
