from dataclasses import dataclass
from enum import Enum

from anre.connection.polymarket.master_client import MasterClient


def __dummy__():
    condition_id = '0x41eda073eeca4071d3a643a527bf8549851ff16c7e4b924a007671cb11920f98'
    self = MarketDataState(condition_id)

    market_info = self.market_info_parser.market_info
    self.get_historical_price()
    self.get_house_order_dict_list()
    self.get_net_mob()
    self.get_top_level_price_dict()


class ActionGateEnum(Enum):
    NONE = 'None'
    CLOSEONLY = 'CloseOnly'
    NOTRADE = 'NoTrade'


@dataclass
class TradingState:
    is_pending_actions: bool = False
    position_gate_state: PositionGateStateEnum = PositionGateStateEnum.NONE


class StrategyBox:
    pass


def __dummy__():
    master_client = MasterClient()

    # master_client.clob_client.cancel_orders_all()

    # end_date_min = datetime.datetime.now() + datetime.timedelta(days=20)
    # market_info_list = master_client.gamma_client.get_market_info_list(
    #     limit=300, active=True, closed=False, end_date_min=end_date_min
    # )

    # slug = "will-zohran-madanis-vote-share-be-less-than-24-in-the-first-round-of-the-nyc-democratic-mayoral-primary"
    # slug = "will-iran-strike-gulf-oil-facilities-before-september"
    slug = "russia-x-ukraine-ceasefire-before-october"
    res = master_client.gamma_client.get_market_info_list(
        slug=slug,
    )
    assert len(res) == 1
    market_info = res[0]
    condition_id = market_info['conditionId']

    master_client.clob_client.get_single_market_info(condition_id=condition_id)

    master_client.clob_client.get_house_order_dict_list()
    #   'market': '0x140167d871a5f240e42dd8a021b03f2777f37589bd56b2c761c9b2bc8e2826f1',
    #   'asset_id': '23936405301368733389536574829640272390080862024402654321653331008041129806355',

    #   'market': '0xdaf2b4abb3e232c7cdc75a86d0018db39a071f1be40e68bf0b3085637420c6f0',
    #   'asset_id': '109054364550013931316084741620575744721889388390339985430626121306120801600493',

    condition_id = '0xdaf2b4abb3e232c7cdc75a86d0018db39a071f1be40e68bf0b3085637420c6f0'

    MasterClient.gamma_client.get_market_info_list(condition_ids=condition_id)

    MasterClient.clob_client.get_single_market_info(condition_id=condition_id)

    order_dict_list = MasterClient.clob_client.get_house_order_dict_list(condition_id=condition_id)
    order_id_list = [item['id'] for item in order_dict_list]
    MasterClient.clob_client.is_order_scoring(order_id=order_id_list[0])
