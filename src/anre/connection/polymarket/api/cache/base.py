from dataclasses import dataclass, field

from sortedcontainers import SortedDict


@dataclass
class Book1000:
    """Limit order book for any asset. Price and sice are multiplied by 1000 and converted to int

    It can be market supply or our contribution into supply
    """

    bids: SortedDict[int, int] = field(default_factory=SortedDict)
    asks: SortedDict[int, int] = field(default_factory=SortedDict)

    @classmethod
    def new_from_native_prices(
        cls, bids: list[dict[str, float | str]], asks: list[dict[str, float | str]]
    ):
        bids = SortedDict({
            int(float(bid['price']) * 1000): int(float(bid['size']) * 1000) for bid in bids
        })
        asks = SortedDict({
            int(float(ask['price']) * 1000): int(float(ask['size']) * 1000) for ask in asks
        })
        return cls(bids=bids, asks=asks)

    def update_overwrite(self, price: float, size: float, side: str):
        size1000 = int(size * 1000)
        price1000 = int(price * 1000)
        if side == 'BUY':
            if size1000 > 0:
                self.bids[price1000] = size1000
            else:
                self.bids.pop(price1000, None)
        elif side == 'ASK':
            if size1000 > 0:
                self.asks[price1000] = size1000
            else:
                self.asks.pop(price1000, None)
        else:
            raise ValueError(f'unknown side: {side}')

    def update_add(self, price: float, size: float, side: str):
        size1000 = int(size * 1000)
        price1000 = int(price * 1000)
        if side == 'BUY':
            if price1000 in self.bids:
                self.bids[price1000] += size1000
            else:
                self.bids[price1000] = size1000
        elif side == 'ASK':
            if price1000 in self.asks:
                self.asks[price1000] += size1000
            else:
                self.asks[price1000] = size1000
        else:
            raise ValueError(f'unknown side: {side}')

    def __post_init__(self):
        assert isinstance(self.bids, SortedDict)
        assert isinstance(self.asks, SortedDict)


@dataclass
class AssetBook:
    asset_id: str
    book1000: Book1000 = field(default_factory=Book1000)


@dataclass
class MarketOrderBook:
    condition_id: str
    yes_asset_book: AssetBook
    no_asset_book: AssetBook

    @classmethod
    def new(cls, condition_id: str, yes_asset_id: str, no_asset_id: str):
        yes_asset_book = AssetBook(asset_id=yes_asset_id)
        no_asset_book = AssetBook(asset_id=no_asset_id)
        return cls(
            condition_id=condition_id, yes_asset_book=yes_asset_book, no_asset_book=no_asset_book
        )

    @classmethod
    def new_from_clob_market_info_dict(cls, clob_market_info_dict: dict):
        assert isinstance(clob_market_info_dict, dict), (
            f'clob_market_dict is not dict. It is: {clob_market_info_dict}'
        )
        yes_asset_ids = [
            el['token_id'] for el in clob_market_info_dict['tokens'] if el['outcome'] == 'Yes'
        ]
        assert len(yes_asset_ids) == 1, (
            f'clob_market_dict does not have exactly one yes asset. It has: {yes_asset_id}'
        )
        yes_asset_id = yes_asset_ids[0]
        no_asset_ids = [
            el['token_id'] for el in clob_market_info_dict['tokens'] if el['outcome'] == 'No'
        ]
        assert len(no_asset_ids) == 1, (
            f'clob_market_dict does not have exactly one no asset. It has: {no_asset_id}'
        )
        no_asset_id = no_asset_ids[0]
        return cls.new(
            condition_id=clob_market_info_dict['condition_id'],
            yes_asset_id=yes_asset_id,
            no_asset_id=no_asset_id,
        )
