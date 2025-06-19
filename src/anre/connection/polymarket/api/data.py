from dataclasses import dataclass

import requests
from requests import Response

from anre.config.config import config as anre_config
from anre.connection.polymarket.api.types import HouseTradeRec


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
    takerOnly: bool = False
    filterType: str = None
    filterAmount: int | float = None
    market: str = None
    side: str = None


def request(endpoint: str, method: str, headers=None, data=None, params=None):
    try:
        resp = requests.request(
            method=method,
            url=endpoint,
            headers=headers,
            json=(data if data else None),
            params=params,
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
    _house_address = anre_config.cred.get_polymarket_creds()['address']

    def get_user_position_dict_list(
        self, user: str, limit: int = None, condition_id: str = None, **kwargs
    ) -> list[dict]:
        # this is not exactly clob, but let it be
        params = PositionsArgs(user=user, limit=limit, market=condition_id, **kwargs)
        params = {key: value for key, value in params.__dict__.items() if value is not None}
        url = self._url + "/positions"
        return get(url, params=params)

    def get_house_position_dict_list(self, **kwargs) -> list[dict]:
        return self.get_user_position_dict_list(user=self._house_address, **kwargs)

    def get_user_trade_dict_list(
        self, user: str, limit: int = None, condition_id: str = None, **kwargs
    ) -> list[dict]:
        # this is not exactly clob, but let it be
        params = TradesArgs(user=user, limit=limit, market=condition_id, **kwargs)
        params = {key: value for key, value in params.__dict__.items() if value is not None}
        url = self._url + "/trades"
        return get(url, params=params)

    def get_house_trade_dict_list(self, **kwargs) -> list[dict]:
        return self.get_user_trade_dict_list(user=self._house_address, **kwargs)

    @staticmethod
    def parse_house_trade_dict_list(house_trade_dict_list: list[dict]) -> dict[str, HouseTradeRec]:
        def _get_house_trade_rec(date_trade_rec_dict):
            return HouseTradeRec(
                conditionId=date_trade_rec_dict['conditionId'],
                assetId=date_trade_rec_dict['asset'],
                outcome=date_trade_rec_dict['outcome'],
                side=date_trade_rec_dict['side'],
                size=date_trade_rec_dict['size'],
                price=date_trade_rec_dict['price'],
                timestamp=date_trade_rec_dict['timestamp'],
                transactionHash=date_trade_rec_dict['transactionHash'],
            )

        house_trade_rec_dict = {
            date_trade_rec_dict['transactionHash']: _get_house_trade_rec(date_trade_rec_dict)
            for date_trade_rec_dict in house_trade_dict_list
        }
        return house_trade_rec_dict


def __demo__():
    self = DataClient()
    print(self)

    self.get_house_position_dict_list(limit=3)
