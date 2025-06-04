from py_clob_client.client import ClobClient
from py_clob_client.clob_types import (
    ApiCreds,
    AssetType,
    BalanceAllowanceParams,
    OrderArgs,
    OrderType,
)
from py_clob_client.constants import POLYGON
from py_clob_client.order_builder.constants import BUY

from anre.config.config import config as anre_config


def main():
    polymarket_creds = anre_config.cred.get_polymarket_creds()
    client = ClobClient(
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
    client.set_api_creds(api_creds)

    assert client.get_ok() == 'OK'
    client.assert_level_1_auth()
    client.assert_level_2_auth()

    ### see balance (and something)
    collateral = client.get_balance_allowance(
        params=BalanceAllowanceParams(asset_type=AssetType.COLLATERAL)
    )
    print(collateral)

    client.get_trades()
    client.get_orders()

    order_args = OrderArgs(
        price=0.1,
        size=11.0,
        side=BUY,
        token_id="57228898880763735727492085926918264681751972810038288059476693936182848695965",  # Token ID you want to purchase goes here.
    )
    signed_order = client.create_order(order_args)
    resp = client.post_order(signed_order, OrderType.GTC)
    print(resp)

    resp = client.cancel_all()
    print(resp)
