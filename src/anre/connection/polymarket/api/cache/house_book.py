from dataclasses import dataclass, field

from anre.connection.polymarket.api.cache.base import AssetBook as BaseAssetBook
from anre.connection.polymarket.api.cache.base import Book1000
from anre.connection.polymarket.api.cache.base import BoolMarketOrderBook as BaseMarketOrderBook


@dataclass(frozen=False, repr=False)
class HouseAssetBook(BaseAssetBook):
    asset_id: str
    book1000: Book1000 = field(default_factory=Book1000)


@dataclass(frozen=False, repr=False)
class HouseOrderBookCache(BaseMarketOrderBook):
    condition_id: str
    main_asset_book: HouseAssetBook
    counter_asset_book: HouseAssetBook
    _house_live_order_dict: dict[str, dict] = field(default_factory=list)

    def __post_init__(self):
        assert self.main_asset_book.asset_id != self.counter_asset_book.asset_id, (
            f'yes_asset_id and no_asset_id must be different. Got: {self.main_asset_book.asset_id} and {self.counter_asset_book.asset_id}'
        )

    def __eq__(self, other):
        if not isinstance(other, HouseOrderBookCache):
            return False
        return (
            self.condition_id == other.condition_id
            and self.main_asset_book == other.main_asset_book
            and self.counter_asset_book == other.counter_asset_book
        )

    @classmethod
    def new_init(
        cls, condition_id: str, main_asset_id: str, counter_asset_id: str
    ) -> 'HouseOrderBookCache':
        main_asset_book = HouseAssetBook(asset_id=main_asset_id)
        counter_asset_book = HouseAssetBook(asset_id=counter_asset_id)
        return cls(
            condition_id=condition_id,
            main_asset_book=main_asset_book,
            counter_asset_book=counter_asset_book,
        )

    @staticmethod
    def counter_side(side: str) -> str:
        if side == 'BUY':
            return 'SELL'
        elif side == 'SELL':
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
        main_asset_book, counter_asset_book = self._get_asset_books_from_live_orders(
            live_order_dict=live_order_dict
        )
        self.main_asset_book, self.counter_asset_book, self._house_live_order_dict = (
            main_asset_book,
            counter_asset_book,
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
        self.main_asset_book, self.counter_asset_book = self._get_asset_books_from_live_orders(
            live_order_dict=self._house_live_order_dict
        )
        if validate:
            self.validate()

    def _get_asset_books_from_live_orders(self, live_order_dict: dict[str, dict]):
        main_asset_book = HouseAssetBook(asset_id=self.main_asset_book.asset_id)
        counter_asset_book = HouseAssetBook(asset_id=self.counter_asset_book.asset_id)
        # live_order = list(live_order_dict.values())[3]
        for _, live_order in live_order_dict.items():
            assert live_order['market'] == self.condition_id
            assert live_order['status'] == 'LIVE'
            size_remaining = float(live_order['original_size']) - float(live_order['size_matched'])
            price = float(live_order['price'])
            side = live_order['side']
            if live_order['outcome'] == 'Yes':
                # direct
                assert live_order['asset_id'] == self.main_asset_book.asset_id
                main_asset_book.book1000.update_add(price=price, size=size_remaining, side=side)
                # counter
                counter_asset_book.book1000.update_add(
                    price=self.counter_price(price=price),
                    size=size_remaining,
                    side=self.counter_side(side=side),
                )
            elif live_order['outcome'] == 'No':
                # direct
                assert live_order['asset_id'] == self.counter_asset_book.asset_id
                counter_asset_book.book1000.update_add(price=price, size=size_remaining, side=side)
                # counter
                main_asset_book.book1000.update_add(
                    price=self.counter_price(price=price),
                    size=size_remaining,
                    side=self.counter_side(side=side),
                )
            else:
                raise ValueError(f'unknown outcome: {live_order["outcome"]}')
        return main_asset_book, counter_asset_book
