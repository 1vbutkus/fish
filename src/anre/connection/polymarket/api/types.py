from dataclasses import dataclass


@dataclass
class HouseTradeRec:
    conditionId: str
    assetId: str
    outcome: str
    side: str
    size: float
    price: float
    timestamp: int | float

    def __post_init__(self):
        assert self.outcome in ['Yes', 'No']
        assert self.side in ['BUY', 'SELL']
