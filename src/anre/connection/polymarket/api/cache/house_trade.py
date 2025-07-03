from collections.abc import Sequence
from dataclasses import dataclass, field

import pandas as pd

from anre.connection.polymarket.api.clob.parse import ClobTradeParser
from anre.connection.polymarket.api.data import DataClient
from anre.connection.polymarket.api.types import HouseTradeRec
from anre.utils.dataStructure.general import GeneralBaseMutable


@dataclass(frozen=False, repr=False)
class HouseTradeCache(GeneralBaseMutable):
    condition_id: str
    _house_trade_rec_dict: dict[str, HouseTradeRec] = field(default_factory=dict)

    def update_from_clob_trade_dict_list(self, clob_trade_dict_list: list[dict]) -> None:
        trade_rec_dict = ClobTradeParser.parse_house_trade_dict_list(clob_trade_dict_list)
        assert all([
            trade_rec.conditionId == self.condition_id for trade_rec in trade_rec_dict.values()
        ])
        self._house_trade_rec_dict.update(trade_rec_dict)

    def update_from_ws_trade_dict_list(self, ws_trade_dict_list: list[dict]) -> None:
        subset = [el for el in ws_trade_dict_list if el.get('type') == 'TRADE']
        # panasu, kad strukura atitinka
        trade_rec_dict = ClobTradeParser.parse_house_trade_dict_list(subset)
        assert all([
            trade_rec.conditionId == self.condition_id for trade_rec in trade_rec_dict.values()
        ])
        self._house_trade_rec_dict.update(trade_rec_dict)

    def update_from_data_trade_dict_list(self, data_trade_dict_list: list[dict]) -> None:
        trade_rec_dict = DataClient.parse_house_trade_dict_list(data_trade_dict_list)
        self._house_trade_rec_dict.update(trade_rec_dict)

    @staticmethod
    def create_house_trade_df(house_trade_recs: Sequence[HouseTradeRec]) -> pd.DataFrame:
        house_trade_df = pd.DataFrame.from_records([el.__dict__ for el in house_trade_recs])
        return house_trade_df

    def get_house_trade_df(self) -> pd.DataFrame:
        return self.create_house_trade_df(list(self._house_trade_rec_dict.values()))

    def get_position_by_outcome(self) -> tuple[float | int, float | int]:
        yes_position = 0
        no_position = 0
        for trade_rec in self._house_trade_rec_dict.values():
            if trade_rec.status != 'FAILED':
                if trade_rec.outcome == 'Yes':
                    if trade_rec.side == 'BUY':
                        yes_position += trade_rec.size
                    elif trade_rec.side == 'SELL':
                        yes_position -= trade_rec.size
                    else:
                        raise ValueError(f'Unexpected side: {trade_rec.side}')
                elif trade_rec.outcome == 'No':
                    if trade_rec.side == 'BUY':
                        no_position += trade_rec.size
                    elif trade_rec.side == 'SELL':
                        no_position -= trade_rec.size
                    else:
                        raise ValueError(f'Unexpected side: {trade_rec.side}')

        return yes_position, no_position

        # house_trade_df = self.get_house_trade_df()
        # house_trade_df = house_trade_df.loc[lambda df: df['status']!='FAILED']
        # house_trade_df['sideSize'] = house_trade_df['side'].map({'BUY': 1, 'SELL': -1}) * house_trade_df['size']
        # position_by_outcome = house_trade_df.groupby(['outcome'])['sideSize'].sum().to_dict()
        # if 'Yes' not in position_by_outcome:
        #     position_by_outcome['Yes'] = 0
        # if 'No' not in position_by_outcome:
        #     position_by_outcome['No'] = 0
        # return position_by_outcome

    def get_position_consolidated(self) -> int | float:
        yes_position, no_position = self.get_position_by_outcome()
        return yes_position - no_position
