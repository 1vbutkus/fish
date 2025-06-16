from typing import Any

import httpx
import orjson


class GammaClient:
    BASE_URL = "https://gamma-api.polymarket.com"
    MARKETS_PATH = "/markets"
    EVENTS_PATH = "/events"
    POSITIONS_PATH = "/positions"

    def __init__(self):
        self._markets_endpoint = self._generate_endpoint(self.MARKETS_PATH)
        self._events_endpoint = self._generate_endpoint(self.EVENTS_PATH)
        self._positions_endpoint = self._generate_endpoint(self.POSITIONS_PATH)

    def _generate_endpoint(self, path: str) -> str:
        """Generates full API endpoint URL."""
        return f"{self.BASE_URL}{path}"

    def _perform_get_request(
        self, url: str, query_params: dict[str, Any] | None
    ) -> dict | list[dict]:
        """Handles HTTP GET requests and ensures successful responses."""
        if not isinstance(query_params, (dict, type(None))):
            raise TypeError("query_params must be a dictionary")
        response = httpx.get(url, params=query_params or {})
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Error response from API: HTTP {response.status_code}")

    def get_markets_query(self, query_params: dict[str, Any] | None = None) -> list[dict]:
        return self._perform_get_request(self._markets_endpoint, query_params)

    def get_events_query(self, query_params: dict[str, Any] | None = None) -> list[dict]:
        return self._perform_get_request(self._events_endpoint, query_params)

    def get_positions_query(self, query_params: dict[str, Any] | None = None) -> list[dict]:
        return self._perform_get_request(self._positions_endpoint, query_params)

    def get_market(self, market_id: int) -> dict:
        market_url = self._generate_endpoint(f"{self.MARKETS_PATH}/{market_id}")
        return self._perform_get_request(market_url, query_params=None)

    def get_markets(
        self,
        slug: str = None,
        archived: bool = None,
        active: bool = None,
        closed: bool = None,
        limit: int = 20,
        offset: int = 0,
        order: str = None,
        ascending: bool = None,
        **kwargs: Any,
    ) -> list[dict]:
        query_params = {}
        if limit:
            query_params["limit"] = limit
        if offset:
            query_params["offset"] = offset
        if ascending:
            query_params["ascending"] = ascending
        if slug is not None:
            query_params["slug"] = slug
        if archived is not None:
            query_params["archived"] = archived
        if active is not None:
            query_params["active"] = active
        if closed is not None:
            query_params["closed"] = closed
        if order is not None:
            query_params["order"] = order
        query_params.update(kwargs)
        return self.get_markets_query(query_params)

    def get_events(
        self,
        slug: str = None,
        archived: bool = None,
        active: bool = None,
        closed: bool = None,
        limit: int = 20,
        offset: int = 0,
        order: str = None,
        ascending: bool = None,
        **kwargs: Any,
    ) -> list[dict]:
        query_params = {}
        if limit:
            query_params["limit"] = limit
        if offset:
            query_params["offset"] = offset
        if ascending:
            query_params["ascending"] = ascending
        if slug is not None:
            query_params["slug"] = slug
        if archived is not None:
            query_params["archived"] = archived
        if active is not None:
            query_params["active"] = active
        if closed is not None:
            query_params["closed"] = closed
        if order is not None:
            query_params["order"] = order
        query_params.update(kwargs)
        return self.get_events_query(query_params)

    def get_positions(self, user: str, **kwargs: Any):
        query_params = {'user': user}
        query_params.update(kwargs)
        return self.get_positions_query(query_params)


def __demo__():
    gamma = GammaClient()

    markets = gamma.get_markets(limit=100, active=True, closed=False, end_date_min='2025-07-08')
    len(markets)



    asset_ids = [el for market in markets for el in orjson.loads(market['clobTokenIds'])]
    markets[0]

    events = gamma.get_events(slug="what-will-powell-say-during-june-press-conference")
    len(events)

    gamma.get_market('0xc2c0d4a0500a76186568270e28ff3619e7598578d2e90094bb89f2e0371cff0a')


    negative_markets = [market for market in markets if market.get('negRisk')]
    negative_markets[-1]

