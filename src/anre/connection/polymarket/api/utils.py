from typing import Sequence

from anre.connection.polymarket.api.types import HouseTradeRec


def get_position_by_outcome(
    house_trade_recs: Sequence[HouseTradeRec],
) -> tuple[float | int, float | int]:
    yes_position = 0
    no_position = 0
    condition_id = None
    for trade_rec in house_trade_recs:
        if condition_id is None:
            condition_id = trade_rec.conditionId
        assert trade_rec.conditionId == condition_id
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
