import datetime
from typing import Any

import httpx


class GammaClient:
    BASE_URL = "https://gamma-api.polymarket.com"
    MARKETS_PATH = "/markets"
    EVENTS_PATH = "/events"

    def __init__(self):
        self._markets_endpoint = self._generate_endpoint(self.MARKETS_PATH)
        self._events_endpoint = self._generate_endpoint(self.EVENTS_PATH)

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

    # def get_single_market_info(self, market_id: int) -> dict:
    #     market_url = self._generate_endpoint(f"{self.MARKETS_PATH}/{market_id}")
    #     return self._perform_get_request(market_url, query_params=None)

    def get_market_info_list(
        self,
        slug: str = None,
        archived: bool = None,
        active: bool = None,
        closed: bool = None,
        limit: int = 20,
        offset: int = 0,
        order: str = None,
        clob_token_ids: list[str] = None,
        condition_ids: list[str] = None,
        ascending: bool = None,
        start_date_min: str | datetime.datetime = None,
        start_date_max: str | datetime.datetime = None,
        end_date_min: str | datetime.datetime = None,
        end_date_max: str | datetime.datetime = None,
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
        if clob_token_ids is not None:
            query_params["clob_token_ids"] = clob_token_ids
        if condition_ids is not None:
            query_params["condition_ids"] = condition_ids
        if start_date_min is not None:
            query_params["start_date_min"] = (
                start_date_min.strftime("%Y-%m-%dT%H:%M:%SZ")
                if isinstance(start_date_min, datetime.datetime)
                else start_date_min
            )
        if start_date_max is not None:
            query_params["start_date_max"] = (
                start_date_max.strftime("%Y-%m-%dT%H:%M:%SZ")
                if isinstance(start_date_max, datetime.datetime)
                else start_date_max
            )
        if end_date_min is not None:
            query_params["end_date_min"] = (
                end_date_min.strftime("%Y-%m-%dT%H:%M:%SZ")
                if isinstance(end_date_min, datetime.datetime)
                else end_date_min
            )
        if end_date_max is not None:
            query_params["end_date_max"] = (
                end_date_max.strftime("%Y-%m-%dT%H:%M:%SZ")
                if isinstance(end_date_max, datetime.datetime)
                else end_date_max
            )

        query_params.update(kwargs)
        return self.get_markets_query(query_params)

    def get_event_info_list(
        self,
        slug: str = None,
        archived: bool = None,
        active: bool = None,
        closed: bool = None,
        limit: int = 20,
        offset: int = 0,
        order: str = None,
        ascending: bool = None,
        start_date_min: str | datetime.datetime = None,
        start_date_max: str | datetime.datetime = None,
        end_date_min: str | datetime.datetime = None,
        end_date_max: str | datetime.datetime = None,
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
        if start_date_min is not None:
            query_params["start_date_min"] = (
                start_date_min.strftime("%Y-%m-%dT%H:%M:%SZ")
                if isinstance(start_date_min, datetime.datetime)
                else start_date_min
            )
        if start_date_max is not None:
            query_params["start_date_max"] = (
                start_date_max.strftime("%Y-%m-%dT%H:%M:%SZ")
                if isinstance(start_date_max, datetime.datetime)
                else start_date_max
            )
        if end_date_min is not None:
            query_params["end_date_min"] = (
                end_date_min.strftime("%Y-%m-%dT%H:%M:%SZ")
                if isinstance(end_date_min, datetime.datetime)
                else end_date_min
            )
        if end_date_max is not None:
            query_params["end_date_max"] = (
                end_date_max.strftime("%Y-%m-%dT%H:%M:%SZ")
                if isinstance(end_date_max, datetime.datetime)
                else end_date_max
            )

        query_params.update(kwargs)
        return self.get_events_query(query_params)


def __demo__():
    gamma = GammaClient()

    markets = gamma.get_market_info_list(
        limit=100, active=True, closed=False, end_date_min='2025-07-08'
    )
    len(markets)
