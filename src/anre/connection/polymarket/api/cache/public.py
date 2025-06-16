from dataclasses import dataclass, field
from sortedcontainers import SortedDict

from anre.connection.polymarket.api.cache.base import AssetBook as BaseAssetBook
from anre.connection.polymarket.api.cache.base import MarketOrderBook as BaseMarketOrderBook
from anre.connection.polymarket.api.cache.base import Book1000


@dataclass
class PublicAssetBook(BaseAssetBook):
    asset_id: str
    book1000: Book1000 = field(default_factory=Book1000)
    timestamp: float = float(0)
    hash: str = ''

    def update_from_clob_message(self, message: dict):
        assert 'event_type' not in message
        assert message['asset_id'] == self.asset_id, f'message is not for this asset_id. Expected: {self.asset_id}, got: {message["asset_id"]}'
        timestamp = float(message['timestamp'])
        assert timestamp > self.timestamp, f'update message is not newer. Last update: {self.timestamp}, new update: {timestamp}'
        book1000 = Book1000.new_from_native_prices(asks=message['asks'], bids=message['bids'])
        self.book1000 = book1000
        self.timestamp = timestamp
        self.hash = message['hash']


    def update_from_ws_message(self, message: dict):
        assert 'event_type' in message, f'message does not have `event_type`. It is not stream message: {message}'
        event_type = message['event_type']
        if event_type == 'book':
            assert message['asset_id'] == self.asset_id, f'message is not for this asset_id. Expected: {self.asset_id}, got: {message["asset_id"]}'
            timestamp = float(message['timestamp'])
            assert timestamp > self.timestamp, f'update message is not newer. Last update: {self.timestamp}, new update: {timestamp}'
            book1000 = Book1000.new_from_native_prices(asks=message['asks'], bids=message['bids'])
            self.book1000 = book1000
            self.timestamp = timestamp
            self.hash = message['hash']

        elif event_type == 'price_change':
            assert message['asset_id'] == self.asset_id, f'message is not for this asset_id. Expected: {self.asset_id}, got: {message["asset_id"]}'
            timestamp = float(message['timestamp'])
            assert timestamp > self.timestamp, f'update message is not newer. Last update: {self.timestamp}, new update: {timestamp}'

            for change in message['changes']:
                self.book1000.update_overwrite(price=float(change['price']), size=float(change['size']), side=change['side'])

            self.hash = message['hash']
            self.timestamp = timestamp

        else:
            raise ValueError(f'unknown event type: {event_type}')


@dataclass
class PublicMarketOrderBook(BaseMarketOrderBook):
    condition_id: str
    yes_asset_book: PublicAssetBook
    no_asset_book: PublicAssetBook

    def __post_init__(self):
        assert self.yes_asset_book.asset_id != self.no_asset_book.asset_id, f'yes_asset_id and no_asset_id must be different. Got: {self.yes_asset_book.asset_id} and {self.no_asset_book.asset_id}'


    @classmethod
    def new(cls, condition_id: str, yes_asset_id: str, no_asset_id: str):
        yes_asset_book = PublicAssetBook(asset_id=yes_asset_id)
        no_asset_book = PublicAssetBook(asset_id=no_asset_id)
        return cls(condition_id=condition_id, yes_asset_book=yes_asset_book, no_asset_book=no_asset_book)

    def update_from_clob_mob(self, clob_mob: dict):
        assert 'event_type' not in clob_mob
        assert clob_mob['market'] == self.condition_id, f'message is not for this condition_id. Expected: {self.condition_id}, got: {clob_mob["condition_id"]}'
        if clob_mob['asset_id'] == self.yes_asset_book.asset_id:
            self.yes_asset_book.update_from_clob_message(message=clob_mob)
        elif clob_mob['asset_id'] == self.no_asset_book.asset_id:
            self.no_asset_book.update_from_clob_message(message=clob_mob)
        else:
            raise ValueError(f'unknown asset_id: {clob_mob["asset_id"]}')

    def update_from_ws_message(self, ws_message: dict):
        assert 'event_type' in ws_message, f'message does not have `event_type`. It is not stream message: {ws_message}'
        event_type = ws_message['event_type']
        if event_type in ['book', 'price_change']:
            assert ws_message['market'] == self.condition_id, f'message is not for this condition_id. Expected: {self.condition_id}, got: {ws_message["condition_id"]}'
            if ws_message['asset_id'] == self.yes_asset_book.asset_id:
                self.yes_asset_book.update_from_ws_message(message=ws_message)
            elif ws_message['asset_id'] == self.no_asset_book.asset_id:
                self.no_asset_book.update_from_ws_message(message=ws_message)
            else:
                raise ValueError(f'unknown asset_id: {ws_message["asset_id"]}')

        elif event_type == '_internal':
            pass

        elif event_type == 'tick_size_change':
            pass

        else:
            raise ValueError(f'unknown event type: {event_type}')



def __dummy__():
    from anre.config.config import config as anre_config
    from anre.utils.Json.Json import Json

    _file_path = anre_config.path.get_path_to_root_dir('src/anre/connection/polymarket/api/cache/tests/resources/info_step_list.json')
    info_step_list = Json.load(path=_file_path)

    clob_market_info_dict = info_step_list[0]['clob_market_info_dict']

    ### zero step
    clob_mob_list = info_step_list[0]['clob_mob_list']
    clob_public_mob_0_cache = PublicMarketOrderBook.new_from_clob_market_info_dict(clob_market_info_dict=clob_market_info_dict)
    for clob_mob in clob_mob_list:
        clob_public_mob_0_cache.update_from_clob_mob(clob_mob=clob_mob)

    ### first step
    clob_mob_list = info_step_list[1]['clob_mob_list']
    clob_public_mob_1_cache = PublicMarketOrderBook.new_from_clob_market_info_dict(clob_market_info_dict=clob_market_info_dict)
    for clob_mob in clob_mob_list:
        clob_public_mob_1_cache.update_from_clob_mob(clob_mob=clob_mob)

    ws_market_message_list = info_step_list[1]['ws_market_message_list']
    ws_public_mob_1_cache = PublicMarketOrderBook.new_from_clob_market_info_dict(clob_market_info_dict=clob_market_info_dict)
    for ws_message in ws_market_message_list:
        ws_public_mob_1_cache.update_from_ws_message(ws_message=ws_message)

    # patikrinam as ws ir clob info sutampa
    assert clob_public_mob_1_cache == ws_public_mob_1_cache

    # ar yes ir no yra revertinti variantai?
    pairs = zip(
        clob_public_mob_1_cache.yes_asset_book.book1000.bids.items(),
        reversed(clob_public_mob_1_cache.no_asset_book.book1000.asks.items()),
    )
    for yes_i, no_i in pairs:
        assert yes_i[0] + no_i[0] == 1000
        assert yes_i[1] == no_i[1]

