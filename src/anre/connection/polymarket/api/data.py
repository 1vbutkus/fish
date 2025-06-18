import base64
import time
from dataclasses import dataclass
from functools import partial
from typing import Callable, Literal, Optional
from requests import Response
import requests
from py_clob_client.client import ClobClient as ClobInternalClient
from py_clob_client.clob_types import (
    ApiCreds,
    OpenOrderParams,
    OrderArgs,
    OrderType,
    PriceHistoryArgs,
    TradeParams,
)
from py_clob_client.constants import POLYGON
from py_clob_client.order_builder.constants import BUY, SELL

from anre.config.config import config as anre_config



class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp: Response = None, error_msg=None):
        assert resp is not None or error_msg is not None
        if resp is not None:
            self.status_code = resp.status_code
            self.error_msg = self._get_message(resp)
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None

    def _get_message(self, resp: Response):
        try:
            return resp.json()
        except Exception:
            return resp.text

    def __repr__(self):
        return "PolyApiException[status_code={}, error_message={}]".format(
            self.status_code, self.error_msg
        )

    def __str__(self):
        return self.__repr__()


@dataclass
class PositionsArgs:
    user: str
    market: str = None
    sizeThreshold: int | float = None
    redeemable: bool = None
    mergeable: bool = None
    title: str = None
    eventId: str = None
    limit: int = None  # max 500
    offset: int = None
    sortBy: str = None
    sortDirection: str = None


@dataclass
class TradesArgs:
    user: str
    limit: int = None  # max 500
    offset: int = None
    takerOnly: bool = None
    filterType: str = None
    filterAmount: int | float = None
    market: str = None
    side: str = None


def request(endpoint: str, method: str, headers=None, data=None, params=None):
    try:
        resp = requests.request(
            method=method, url=endpoint, headers=headers, json=(data if data else None), params=params
        )
        if resp.status_code != 200:
            raise PolyApiException(resp)

        try:
            return resp.json()
        except requests.JSONDecodeError:
            return resp.text

    except requests.RequestException:
        raise PolyApiException(error_msg="Request exception!")


def get(endpoint, headers=None, data=None, params=None):
    return request(endpoint, "GET", headers, data, params=params)


class DataClient:
    _url = "https://data-api.polymarket.com"
    def __init__(self):
        self._house_user = anre_config.cred.get_polymarket_creds()['contract']

    def get_user_positions(self, user: str, limit: int = None, **kwargs) -> list[dict]:
        # this is not exactly clob, but let it be
        params = PositionsArgs(user=user, limit=limit, **kwargs)
        params = {key: value for key, value in params.__dict__.items() if value is not None}
        url = self._url + "/positions"
        return get(url, params=params)

    def get_house_positions(self, **kwargs):
        return self.get_user_positions(user=self._house_user, **kwargs)

    def get_user_trades(self, user: str, limit: int = None, **kwargs) -> list[dict]:
        # this is not exactly clob, but let it be
        params = TradesArgs(user=user, limit=limit, **kwargs)
        params = {key: value for key, value in params.__dict__.items() if value is not None}
        url = self._url + "/trades"
        return get(url, params=params)

    def get_house_trades(self, **kwargs):
        return self.get_user_trades(user=self._house_user, **kwargs)


def __demo__():
    self = DataClient()
    print(self)

    self.get_house_positions(limit=3)
    self.get_house_trades(limit=3)
