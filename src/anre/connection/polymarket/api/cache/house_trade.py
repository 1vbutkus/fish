from dataclasses import dataclass
from dataclasses import dataclass, field
from collections.abc import Sequence

from cytoolz.itertoolz import deque

from anre.connection.polymarket.api.cache.base import AssetBook as BaseAssetBook
from anre.connection.polymarket.api.cache.base import Book1000
from anre.connection.polymarket.api.cache.base import MarketOrderBook as BaseMarketOrderBook

import pandas as pd

from anre.connection.polymarket.api.clob import ClobClient
from anre.connection.polymarket.api.data import DataClient
from anre.connection.polymarket.api.types import HouseTradeRec
from anre.connection.polymarket.api.types import HouseTradeRec
from anre.utils.dataStructure.general import GeneralBaseMutable


@dataclass(frozen=False, repr=False)
class HouseTradeCache(GeneralBaseMutable):
    condition_id: str
    _house_trade_recs: deque[HouseTradeRec] = field(default_factory=deque)

    def extend(self, house_trade_recs: Sequence[HouseTradeRec]):
        assert all([isinstance(el, HouseTradeRec) for el in house_trade_recs])
        self._house_trade_recs.extend(house_trade_recs)
        return self

    @staticmethod
    def create_house_trade_df(house_trade_rec_list: Sequence[HouseTradeRec]) -> pd.DataFrame:
        house_trade_df = pd.DataFrame.from_records([el.__dict__ for el in house_trade_rec_list])
        return house_trade_df

    def get_house_trade_df(self) -> pd.DataFrame:
        return self.create_house_trade_df(self._house_trade_recs)

    def get_position_by_outcome(self) -> dict:
        house_trade_df = self.get_house_trade_df()
        house_trade_df['sideSize'] = house_trade_df['side'].map({'BUY': 1, 'SELL': -1}) * house_trade_df['size']
        position_by_outcome = house_trade_df.groupby(['outcome'])['sideSize'].sum().to_dict()
        if 'Yes' not in position_by_outcome:
            position_by_outcome['Yes'] = 0
        if 'No' not in position_by_outcome:
            position_by_outcome['No'] = 0
        return position_by_outcome

    def get_position_consolidated(self) -> dict:
        position_by_outcome = self.get_position_by_outcome()
        return position_by_outcome['Yes'] - position_by_outcome['No']


def __dummy__():
    clob_client = ClobClient()
    data_client = DataClient()

    condition_id = '0xae546fe6f033bb5f9f7904bff4dbb142659953229c458ec0d0726d4c0c32f65f'

    position_dict_list = data_client.get_house_position_dict_list(condition_id=condition_id)

    house_trade_dict_list = data_client.get_house_trade_dict_list(condition_id=condition_id)
    house_trade_recs = data_client.parse_house_trade_dict_list(house_trade_dict_list)
    house_trade_cache = HouseTradeCache(condition_id=condition_id)
    house_trade_cache.extend(house_trade_recs)
    house_trade_cache.get_position_by_outcome()
    house_trade_cache.get_position_consolidated()


    house_trade_df = house_trade_cache.get_house_trade_df()
    house_trade_df['sideSize'] = house_trade_df['side'].map({'BUY': 1, 'SELL': -1}) * house_trade_df['size']
    house_trade_df.groupby(['outcome'])['sideSize'].sum().to_dict()



    _res = data_client.get_house_trade_dict_list(condition_id=condition_id)
    data_house_trade_rec_list = data_client.parse_house_trade_dict_list(_res)
    data_house_trade_df = pd.DataFrame.from_records([el.__dict__ for el in data_house_trade_rec_list])

    _res = clob_client.get_house_trade_dict_list(condition_id=condition_id)
    clob_house_trade_rec_list = clob_client.parse_house_trade_dict_list(_res)
    clob_house_trade_df = pd.DataFrame.from_records([el.__dict__ for el in clob_house_trade_rec_list])

    ### assert data it self is matching
    pd.testing.assert_frame_equal(data_house_trade_df.drop(columns=['timestamp']), clob_house_trade_df.drop(columns=['timestamp']))



    data_trade_list = data_client.get_house_trades(condition_id=condition_id, limit=100)
    def _get_house_trade_rec(date_trade_rec_dict):
        return HouseTradeRec(
            conditionId=date_trade_rec_dict['conditionId'],
            assetId=date_trade_rec_dict['asset'],
            outcome=date_trade_rec_dict['outcome'],
            side=date_trade_rec_dict['side'],
            size=date_trade_rec_dict['size'],
            price=date_trade_rec_dict['price'],
            timestamp=date_trade_rec_dict['timestamp'],
        )
    house_trade_rec_list = [_get_house_trade_rec(date_trade_rec_dict) for date_trade_rec_dict in data_trade_list]
    len(house_trade_rec_list)
    house_trade_df = pd.DataFrame.from_records([el.__dict__ for el in house_trade_rec_list])
    house_trade_df['_priceSize'] = house_trade_df['price'] * house_trade_df['size']
    house_trade_df.groupby(['conditionId', 'assetId', 'outcome', 'side'])[['size', '_priceSize']].sum()


    house_address = '0x94e44831dFc1F9F5C1c9216e7C4AF0aF43b43b11'
    # note sitas blogai. Jis grazina visus traidus, kuriuose mes kazkur figuruojam, Kiek teb konkreciai musu dar reikia isiparsinti (priklausomai nuo maker taker
    clob_trade_list = clob_client.get_house_trades(market=condition_id)
    rec_list = []
    # clob_trade_rec_dict = clob_trade_list[-1]


    clob_trade_df = pd.DataFrame.from_records([el.__dict__ for el in rec_list])
    clob_trade_df['_priceSize'] = clob_trade_df['price'] * clob_trade_df['size']
    clob_trade_df.groupby(['conditionId', 'assetId', 'outcome', 'side'])[['size', '_priceSize']].sum()





    # trades_all = data_client.get_house_trades()
    # trades = [el for el in trades_all if el['conditionId'] == condition_id]
    _fields = ['conditionId', 'asset', 'outcome', 'status', 'side', 'size', 'price', 'timestamp']  # order_id
    recs = [{k: v for k, v in el.items() if k in _fields} for el in trades]
    trade_df = pd.DataFrame.from_records(recs)
    trade_df['size'] = trade_df['size'].astype(float)
    trade_df['price'] = trade_df['price'].astype(float)
    trade_df['_priceSize'] = trade_df['price'] * trade_df['size']
    trade_df.groupby(['conditionId', 'asset', 'side', 'outcome'])[['size', '_priceSize']].sum()


    ###



    _fields = ['market', 'asset_id', 'outcome', 'status', 'side', 'size', 'price', 'match_time']
    recs = [{k: v for k,v in el.items() if k in _fields} for el in trades]
    trade_df = pd.DataFrame.from_records(recs)
    trade_df['size'] = trade_df['size'].astype(float)
    trade_df['price'] = trade_df['price'].astype(float)
    trade_df['_priceSize'] = trade_df['price'] * trade_df['size']
    # tako only confirmed = trade_df[trade_df['status'] == 'confirmed']
    trade_df.groupby(['market', 'asset_id', 'side', 'outcome'])[['size', '_priceSize']].sum()

    el = trades[0]
    {k: v for k, v in el.items() if k in _fields}

    clob_trade_list[0]
    clob_trade_list[-1]