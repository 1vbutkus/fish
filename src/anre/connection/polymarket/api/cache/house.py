from dataclasses import dataclass, field

from anre.connection.polymarket.api.cache.base import AssetBook as BaseAssetBook
from anre.connection.polymarket.api.cache.base import Book1000
from anre.connection.polymarket.api.cache.base import MarketOrderBook as BaseMarketOrderBook


@dataclass
class HouseAssetBook(BaseAssetBook):
    asset_id: str
    book1000: Book1000 = field(default_factory=Book1000)


@dataclass
class HouseOrderBook(BaseMarketOrderBook):
    condition_id: str
    yes_asset_book: HouseAssetBook
    no_asset_book: HouseAssetBook
    house_live_order_dict: dict[str, dict] = field(default_factory=list)

    def __post_init__(self):
        assert self.yes_asset_book.asset_id != self.no_asset_book.asset_id, (
            f'yes_asset_id and no_asset_id must be different. Got: {self.yes_asset_book.asset_id} and {self.no_asset_book.asset_id}'
        )

    def __eq__(self, other):
        if not isinstance(other, HouseOrderBook):
            return False
        return (
            self.condition_id == other.condition_id
            and self.yes_asset_book == other.yes_asset_book
            and self.no_asset_book == other.no_asset_book
        )

    @classmethod
    def new(cls, condition_id: str, yes_asset_id: str, no_asset_id: str):
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

    def update_from_clob_house_order_list(self, clob_house_order_list: list[dict]):
        live_order_dict = {order['id']: order for order in clob_house_order_list}
        yes_asset_book, no_asset_book = self.get_asset_books_from_live_orders(
            live_order_dict=live_order_dict
        )
        self.yes_asset_book, self.no_asset_book, self.house_live_order_dict = (
            yes_asset_book,
            no_asset_book,
            live_order_dict,
        )

    def update_from_ws_messages(self, ws_message_list: list[dict]):
        for ws_message in ws_message_list:
            if ws_message["event_type"] in ["order", "trade"]:
                if ws_message['status'] == 'LIVE':
                    self.house_live_order_dict[ws_message['id']] = ws_message
                else:
                    self.house_live_order_dict.pop(ws_message['id'], None)
            elif ws_message["event_type"] == "_internal":
                pass
            else:
                raise ValueError(f'unknown event type: {ws_message["event_type"]}')
        self.yes_asset_book, self.no_asset_book = self.get_asset_books_from_live_orders(
            live_order_dict=self.house_live_order_dict
        )

    def get_asset_books_from_live_orders(self, live_order_dict: dict[str, dict]):
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


def __dummy__():
    from anre.config.config import config as anre_config
    from anre.utils.Json.Json import Json

    _file_path = anre_config.path.get_path_to_root_dir(
        'src/anre/connection/polymarket/api/cache/tests/resources/info_step_list.json'
    )
    info_step_list = Json.load(path=_file_path)

    clob_market_info_dict = info_step_list[0]['clob_market_info_dict']

    clob_house_order_list = info_step_list[1]['clob_house_order_list']
    clob_house_order_book_cache = HouseOrderBook.new_from_clob_market_info_dict(
        clob_market_info_dict=clob_market_info_dict
    )
    clob_house_order_book_cache.update_from_clob_house_order_list(
        clob_house_order_list=clob_house_order_list
    )

    clob_house_order_list = info_step_list[2]['clob_house_order_list']
    self = clob_house_order_book_cache = HouseOrderBook.new_from_clob_market_info_dict(
        clob_market_info_dict=clob_market_info_dict
    )
    clob_house_order_book_cache.update_from_clob_house_order_list(
        clob_house_order_list=clob_house_order_list
    )

    #
    ws_house_order_book_cache = HouseOrderBook.new_from_clob_market_info_dict(
        clob_market_info_dict=clob_market_info_dict
    )
    clob_house_order_list = info_step_list[1]['clob_house_order_list']
    ws_house_message_list = info_step_list[2]['ws_house_message_list']
    ws_house_order_book_cache.update_from_clob_house_order_list(
        clob_house_order_list=clob_house_order_list
    )
    ws_house_order_book_cache.update_from_ws_messages(ws_message_list=ws_house_message_list)

    assert ws_house_order_book_cache == clob_house_order_book_cache

    # patikrinti ar reverso logikagalioja
    pairs = zip(
        ws_house_order_book_cache.yes_asset_book.book1000.bids.items(),
        reversed(ws_house_order_book_cache.no_asset_book.book1000.asks.items()),
    )
    for yes_i, no_i in list(pairs):
        assert yes_i[0] + no_i[0] == 1000
        assert yes_i[1] == no_i[1]
