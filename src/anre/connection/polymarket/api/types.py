from dataclasses import dataclass

from anre.utils.dataStructure.general import GeneralBaseFrozen


@dataclass
class HouseTradeRec:
    conditionId: str
    assetId: str
    outcome: str
    side: str
    size: float
    price: float
    timestamp: int | float
    transactionHash: str
    status: str = 'UNKNOWN'

    def __post_init__(self):
        assert self.outcome in ['Yes', 'No']
        assert self.side in ['BUY', 'SELL']


@dataclass(frozen=True, repr=False)
class BoolMarketCred(GeneralBaseFrozen):
    condition_id: str
    yes_asset_id: str
    no_asset_id: str
