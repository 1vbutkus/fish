from copy import deepcopy
from dataclasses import dataclass, field

from sortedcontainers import SortedDict

from anre.utils.dataStructure.general import GeneralBaseMutable


@dataclass(frozen=False, repr=False)
class Book1000(GeneralBaseMutable):
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
            int(round(float(bid['price']) * 1000)): int(round(float(bid['size']) * 1000))
            for bid in bids
        })
        asks = SortedDict({
            int(round(float(ask['price']) * 1000)): int(round(float(ask['size']) * 1000))
            for ask in asks
        })
        return cls(bids=bids, asks=asks)

    def update_overwrite(self, price: float, size: float, side: str):
        size1000 = int(round(size * 1000))
        price1000 = int(round(price * 1000))
        if side == 'BUY':
            if size1000 > 0:
                self.bids[price1000] = size1000
            else:
                self.bids.pop(price1000, None)
        elif side == 'SELL':
            if size1000 > 0:
                self.asks[price1000] = size1000
            else:
                self.asks.pop(price1000, None)
        else:
            raise ValueError(f'unknown side: {side}')

    def update_add(self, price: float, size: float, side: str):
        size1000 = int(round(size * 1000))
        price1000 = int(round(price * 1000))
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

    def remove_zero_size_records(self):
        for price in list(self.bids.keys()):
            if self.bids[price] == 0:
                self.bids.pop(price, None)
        for price in list(self.asks.keys()):
            if self.asks[price] == 0:
                self.asks.pop(price, None)

    def __post_init__(self):
        assert isinstance(self.bids, SortedDict)
        assert isinstance(self.asks, SortedDict)


@dataclass(frozen=False, repr=False)
class AssetBook(GeneralBaseMutable):
    asset_id: str
    book1000: Book1000 = field(default_factory=Book1000)


@dataclass(frozen=False, repr=False)
class MarketOrderBook(GeneralBaseMutable):
    condition_id: str
    yes_asset_book: AssetBook
    no_asset_book: AssetBook

    def copy(self) -> 'MarketOrderBook':
        return deepcopy(self)

    def equals_book_values(self, other: 'MarketOrderBook') -> bool:
        return (
            self.yes_asset_book.book1000 == other.yes_asset_book.book1000
            and self.no_asset_book.book1000 == other.no_asset_book.book1000
        )

    @classmethod
    def new_init(cls, condition_id: str, yes_asset_id: str, no_asset_id: str) -> 'MarketOrderBook':
        yes_asset_book = AssetBook(asset_id=yes_asset_id)
        no_asset_book = AssetBook(asset_id=no_asset_id)
        return cls(
            condition_id=condition_id, yes_asset_book=yes_asset_book, no_asset_book=no_asset_book
        )

    def _validate_book_symetry(self):
        assert len(self.yes_asset_book.book1000.bids) == len(self.no_asset_book.book1000.asks)
        pairs = zip(
            self.yes_asset_book.book1000.bids.items(),
            reversed(self.no_asset_book.book1000.asks.items()),
        )
        for yes_i, no_i in pairs:
            assert yes_i[0] + no_i[0] == 1000
            assert yes_i[1] == no_i[1]

        assert len(self.yes_asset_book.book1000.asks) == len(self.no_asset_book.book1000.bids)
        pairs = zip(
            self.yes_asset_book.book1000.asks.items(),
            reversed(self.no_asset_book.book1000.bids.items()),
        )
        for yes_i, no_i in pairs:
            assert yes_i[0] + no_i[0] == 1000
            assert yes_i[1] == no_i[1]

    def validate(self):
        self._validate_book_symetry()

    def sub(self, other: 'MarketOrderBook', validate: bool = True) -> 'MarketOrderBook':
        temp = self.copy()

        pairs = zip(
            (
                other.yes_asset_book.book1000.bids,
                other.yes_asset_book.book1000.asks,
                other.no_asset_book.book1000.bids,
                other.no_asset_book.book1000.asks,
            ),
            (
                temp.yes_asset_book.book1000.bids,
                temp.yes_asset_book.book1000.asks,
                temp.no_asset_book.book1000.bids,
                temp.no_asset_book.book1000.asks,
            ),
        )
        for other_dict, temp_dict in pairs:
            for price, value in other_dict.items():
                if price in temp_dict:
                    temp_dict[price] -= value
                else:
                    temp_dict[price] = -value

        temp.yes_asset_book.book1000.remove_zero_size_records()
        temp.no_asset_book.book1000.remove_zero_size_records()

        instance = self.__class__(
            condition_id=temp.condition_id,
            yes_asset_book=temp.yes_asset_book,
            no_asset_book=temp.no_asset_book,
        )
        if validate:
            instance.validate()
        return instance
