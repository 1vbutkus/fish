from dataclasses import dataclass, field

from anre.connection.polymarket.api.cache.base import AssetBook as BaseAssetBook
from anre.connection.polymarket.api.cache.base import Book1000
from anre.connection.polymarket.api.cache.base import MarketOrderBook as BaseMarketOrderBook


@dataclass(frozen=False, repr=False)
class HouseAssetBook(BaseAssetBook):
    asset_id: str
    book1000: Book1000 = field(default_factory=Book1000)


@dataclass(frozen=False, repr=False)
class HouseOrderBookCache(BaseMarketOrderBook):
    condition_id: str
    yes_asset_book: HouseAssetBook
    no_asset_book: HouseAssetBook
    _house_live_order_dict: dict[str, dict] = field(default_factory=list)

    def __post_init__(self):
        assert self.yes_asset_book.asset_id != self.no_asset_book.asset_id, (
            f'yes_asset_id and no_asset_id must be different. Got: {self.yes_asset_book.asset_id} and {self.no_asset_book.asset_id}'
        )

    def __eq__(self, other):
        if not isinstance(other, HouseOrderBookCache):
            return False
        return (
            self.condition_id == other.condition_id
            and self.yes_asset_book == other.yes_asset_book
            and self.no_asset_book == other.no_asset_book
        )

    @classmethod
    def new_init(
        cls, condition_id: str, yes_asset_id: str, no_asset_id: str
    ) -> 'HouseOrderBookCache':
        yes_asset_book = HouseAssetBook(asset_id=yes_asset_id)
        no_asset_book = HouseAssetBook(asset_id=no_asset_id)
        return cls(
            condition_id=condition_id, yes_asset_book=yes_asset_book, no_asset_book=no_asset_book
        )

    @staticmethod
    def counter_side(side: str) -> str:
        if side == 'BUY':
            return 'ASK'
        elif side == 'ASK':
            return 'BUY'
        else:
            raise ValueError(f'unknown side: {side}')

    @staticmethod
    def counter_price(price: float) -> float:
        return 1 - price

    def update_reset_from_clob_house_order_list(
        self, clob_house_order_list: list[dict], validate: bool = True
    ):
        live_order_dict = {order['id']: order for order in clob_house_order_list}
        yes_asset_book, no_asset_book = self._get_asset_books_from_live_orders(
            live_order_dict=live_order_dict
        )
        self.yes_asset_book, self.no_asset_book, self._house_live_order_dict = (
            yes_asset_book,
            no_asset_book,
            live_order_dict,
        )
        if validate:
            self.validate()

    def update_iteration_from_ws_message_list(
        self, ws_message_list: list[dict], validate: bool = True
    ):
        for ws_message in ws_message_list:
            if ws_message["event_type"] in ["order", "trade"]:
                if ws_message['status'] == 'LIVE':
                    self._house_live_order_dict[ws_message['id']] = ws_message
                else:
                    self._house_live_order_dict.pop(ws_message['id'], None)
            elif ws_message["event_type"] == "_internal":
                pass
            else:
                raise ValueError(f'unknown event type: {ws_message["event_type"]}')
        self.yes_asset_book, self.no_asset_book = self._get_asset_books_from_live_orders(
            live_order_dict=self._house_live_order_dict
        )
        if validate:
            self.validate()

    def _get_asset_books_from_live_orders(self, live_order_dict: dict[str, dict]):
        yes_asset_book = HouseAssetBook(asset_id=self.yes_asset_book.asset_id)
        no_asset_book = HouseAssetBook(asset_id=self.no_asset_book.asset_id)
        # live_order = list(live_order_dict.values())[3]
        for _, live_order in live_order_dict.items():
            assert live_order['market'] == self.condition_id
            assert live_order['status'] == 'LIVE'
            size_remaining = float(live_order['original_size']) - float(live_order['size_matched'])
            price = float(live_order['price'])
            side = live_order['side']
            if live_order['outcome'] == 'Yes':
                # direct
                assert live_order['asset_id'] == self.yes_asset_book.asset_id

                yes_asset_book.book1000.update_add(price=price, size=size_remaining, side=side)
                # counter
                no_asset_book.book1000.update_add(
                    price=self.counter_price(price=price),
                    size=size_remaining,
                    side=self.counter_side(side=side),
                )
            elif live_order['outcome'] == 'No':
                # direct
                assert live_order['asset_id'] == self.no_asset_book.asset_id
                no_asset_book.book1000.update_add(price=price, size=size_remaining, side=side)
                # counter
                yes_asset_book.book1000.update_add(
                    price=self.counter_price(price=price),
                    size=size_remaining,
                    side=self.counter_side(side=side),
                )
            else:
                raise ValueError(f'unknown outcome: {live_order["outcome"]}')
        return yes_asset_book, no_asset_book
