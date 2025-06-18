import pandas as pd

from anre.connection.polymarket.api.clob import ClobClient
from anre.connection.polymarket.api.data import DataClient


def __dummy__():
    clob_client = ClobClient()
    data_client = DataClient()

    condition_id = '0xae546fe6f033bb5f9f7904bff4dbb142659953229c458ec0d0726d4c0c32f65f'

    positions = data_client.get_house_positions(condition_id=condition_id)

    trades = data_client.get_house_trades(condition_id=condition_id, limit=100)   #kazkas negerai su situo
    # trades_all = data_client.get_house_trades()
    # trades = [el for el in trades_all if el['conditionId'] == condition_id]
    _fields = ['conditionId', 'asset', 'outcome', 'status', 'side', 'size', 'price', 'timestamp']
    recs = [{k: v for k, v in el.items() if k in _fields} for el in trades]
    trade_df = pd.DataFrame.from_records(recs)
    trade_df['size'] = trade_df['size'].astype(float)
    trade_df['price'] = trade_df['price'].astype(float)
    trade_df['_priceSize'] = trade_df['price'] * trade_df['size']
    trade_df.groupby(['conditionId', 'asset', 'side', 'outcome'])[['size', '_priceSize']].sum()


    ###


    # note sitas blogai. Jis grazina visus traidus, kuriuose mes kazkur figuruojam, Kiek teb konkreciai musu dar reikia isiparsinti (priklausomai nuo maker taker
    trades = clob_client.get_house_trades(market=condition_id)
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
