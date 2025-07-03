import datetime
from typing import Optional

from anre.config.config import config as anre_config
from anre.connection.polymarket.api.types import BoolMarketCred, HouseTradeRec
from anre.utils.time.convert import Convert as TimeConvert


class ClobMarketInfoParser:
    def __init__(self, market_info: dict) -> None:
        self.market_info = market_info

    def __getattr__(self, name):
        # This will be called only for attributes that are not defined as properties
        if name in self.market_info:
            return self.market_info[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    @property
    def is_market_bool(self) -> bool:
        return self.get_is_market_bool(self.market_info)

    @property
    def bool_market_cred(self) -> BoolMarketCred:
        return self.get_bool_market_cred(self.market_info)

    @property
    def bool_market_cred(self) -> BoolMarketCred:
        return self.get_bool_market_cred(self.market_info)

    @property
    def accepting_order_dt(self) -> datetime.datetime:
        return TimeConvert.str2dt(self.market_info['accepting_order_timestamp'])

    @property
    def tick1000(self) -> int:
        return max(1, int(round(self.market_info['minimum_tick_size'] * 1000)))

    @property
    def minimum_order_size(self) -> int:
        return self.market_info['minimum_order_size']

    @property
    def game_start_dt(self) -> Optional[datetime.datetime]:
        game_start_time = self.self.market_info['game_start_time']
        if game_start_time is not None:
            return TimeConvert.str2dt(game_start_time)
        return None

    @property
    def end_dt(self) -> datetime.datetime:
        return TimeConvert.str2dt(self.market_info['end_date_iso'])

    @classmethod
    def get_is_market_bool(cls, market_info: dict) -> bool:
        tokens = market_info['tokens']
        if len(tokens) == 2:
            outcomes = set([item['outcome'] for item in tokens])
            if outcomes == {'Yes', 'No'}:
                return True
        return False

    @classmethod
    def get_bool_market_cred(cls, market_info: dict) -> BoolMarketCred:
        assert isinstance(market_info, dict), f'market_info is not dict. It is: {market_info}'
        yes_asset_ids = [el['token_id'] for el in market_info['tokens'] if el['outcome'] == 'Yes']
        assert len(yes_asset_ids) == 1, (
            f'market_info does not have exactly one yes asset. It has: {yes_asset_ids}'
        )
        yes_asset_id = yes_asset_ids[0]
        no_asset_ids = [el['token_id'] for el in market_info['tokens'] if el['outcome'] == 'No']
        assert len(no_asset_ids) == 1, (
            f'clob_market_dict does not have exactly one no asset. It has: {no_asset_ids}'
        )
        no_asset_id = no_asset_ids[0]
        market_order_book_cred = BoolMarketCred(
            condition_id=market_info['condition_id'],
            main_asset_id=yes_asset_id,
            counter_asset_id=no_asset_id,
        )
        return market_order_book_cred


class ClobTradeParser:
    _house_address = anre_config.cred.get_polymarket_creds()['address']

    @classmethod
    def parse_house_trade_dict_list(cls, trade_dict_list: list[dict]) -> dict[str, HouseTradeRec]:
        rec_dict = {}
        for trade_dict in trade_dict_list:
            if trade_dict['status'] != 'FAILED':
                if trade_dict['trader_side'] == 'MAKER':
                    assert trade_dict['maker_address'] != cls._house_address
                    for sub_dict in trade_dict['maker_orders']:
                        if sub_dict['maker_address'] == cls._house_address:
                            rec = HouseTradeRec(
                                conditionId=trade_dict['market'],
                                assetId=sub_dict['asset_id'],
                                timestamp=int(trade_dict['match_time']),
                                size=float(sub_dict['matched_amount']),
                                price=float(sub_dict['price']),
                                outcome=sub_dict['outcome'],
                                side=sub_dict['side'],
                                transactionHash=trade_dict['transaction_hash'],
                                status=trade_dict['status'],
                            )
                            rec_dict[rec.transactionHash] = rec
                elif trade_dict['trader_side'] == 'TAKER':
                    rec = HouseTradeRec(
                        conditionId=trade_dict['market'],
                        assetId=trade_dict['asset_id'],
                        timestamp=int(trade_dict['match_time']),
                        size=float(trade_dict['size']),
                        price=float(trade_dict['price']),
                        outcome=trade_dict['outcome'],
                        side=trade_dict['side'],
                        transactionHash=trade_dict['transaction_hash'],
                        status=trade_dict['status'],
                    )
                    rec_dict[rec.transactionHash] = rec
        return rec_dict
