from typing import Optional

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import (
    ApiCreds,
)
from py_clob_client.constants import POLYGON

from anre.config.config import config as anre_config


class MasterClient:
    _api_client_cls: Optional[ClobClient] = None

    def __init__(self):
        if self._api_client_cls is None:
            self._api_client_cls = self._create_api_client()
        assert isinstance(self._api_client_cls, ClobClient)
        self._api_client: ClobClient = self._api_client_cls

    def _create_api_client(self):
        polymarket_creds = anre_config.cred.get_polymarket_creds()
        api_client = ClobClient(
            host=polymarket_creds['host'],
            key=polymarket_creds['pk'],
            chain_id=POLYGON,
            signature_type=1,
            funder=polymarket_creds['contract'],
        )
        api_creds = ApiCreds(
            api_key=polymarket_creds['ApiCreds']['api_key'],
            api_secret=polymarket_creds['ApiCreds']['api_secret'],
            api_passphrase=polymarket_creds['ApiCreds']['api_passphrase'],
        )
        # api_creds = client.create_or_derive_api_creds()
        api_client.set_api_creds(api_creds)
        return api_client

    def cancel_all(self):
        self._api_client.cancel_all()


def __dummy__():
    self = MasterClient()

    self._api_client.get_markets(market_slug='russia-x-ukraine-ceasefire-before-july')
