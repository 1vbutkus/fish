from dataclasses import dataclass, field

from sortedcontainers import SortedDict


@dataclass
class LimitOrderBook1000:
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

    def update_single(self, price: float, size: float, side: str):
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

    def __post_init__(self):
        assert isinstance(self.bids, SortedDict)
        assert isinstance(self.asks, SortedDict)


@dataclass
class AssetBook:
    asset_id: str
    timestamp: float = float(0)
    hash: str = ''
    lob1000: LimitOrderBook1000 = field(default_factory=LimitOrderBook1000)

    def update_from_clob_message(self, message: dict):
        assert 'event_type' not in message
        assert message['asset_id'] == self.asset_id, (
            f'message is not for this asset_id. Expected: {self.asset_id}, got: {message["asset_id"]}'
        )
        timestamp = float(message['timestamp'])
        assert timestamp > self.timestamp, (
            f'update message is not newer. Last update: {self.timestamp}, new update: {timestamp}'
        )
        lob = LimitOrderBook1000.new_from_native_prices(asks=message['asks'], bids=message['bids'])
        self.lob1000 = lob
        self.timestamp = timestamp
        self.hash = message['hash']

    def update_from_ws_message(self, message: dict):
        assert 'event_type' in message, (
            f'message does not have `event_type`. It is not stream message: {message}'
        )
        event_type = message['event_type']
        if event_type == 'book':
            assert message['asset_id'] == self.asset_id, (
                f'message is not for this asset_id. Expected: {self.asset_id}, got: {message["asset_id"]}'
            )
            timestamp = float(message['timestamp'])
            assert timestamp > self.timestamp, (
                f'update message is not newer. Last update: {self.timestamp}, new update: {timestamp}'
            )
            lob = LimitOrderBook1000.new_from_native_prices(
                asks=message['asks'], bids=message['bids']
            )
            self.lob1000 = lob
            self.timestamp = timestamp
            self.hash = message['hash']

        elif event_type == 'price_change':
            assert message['asset_id'] == self.asset_id, (
                f'message is not for this asset_id. Expected: {self.asset_id}, got: {message["asset_id"]}'
            )
            timestamp = float(message['timestamp'])
            assert timestamp > self.timestamp, (
                f'update message is not newer. Last update: {self.timestamp}, new update: {timestamp}'
            )

            for change in message['changes']:
                self.lob1000.update_single(
                    price=float(change['price']), size=float(change['size']), side=change['side']
                )

            self.hash = message['hash']
            self.timestamp = timestamp

        else:
            raise ValueError(f'unknown event type: {event_type}')


@dataclass
class PublicMarketBook:
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

    def update_from_clob_mob(self, clob_mob: dict):
        assert 'event_type' not in clob_mob
        assert clob_mob['market'] == self.condition_id, (
            f'message is not for this condition_id. Expected: {self.condition_id}, got: {clob_mob["condition_id"]}'
        )
        if clob_mob['asset_id'] == self.yes_asset_book.asset_id:
            self.yes_asset_book.update_from_clob_message(message=clob_mob)
        elif clob_mob['asset_id'] == self.no_asset_book.asset_id:
            self.no_asset_book.update_from_clob_message(message=clob_mob)
        else:
            raise ValueError(f'unknown asset_id: {clob_mob["asset_id"]}')

    def update_from_ws_message(self, ws_message: dict):
        assert 'event_type' in ws_message, (
            f'message does not have `event_type`. It is not stream message: {ws_message}'
        )
        event_type = ws_message['event_type']
        if event_type in ['book', 'price_change']:
            assert ws_message['market'] == self.condition_id, (
                f'message is not for this condition_id. Expected: {self.condition_id}, got: {ws_message["condition_id"]}'
            )
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


@dataclass
class HouseOrderBook:
    condition_id: str
    yes_asset_book: AssetBook
    no_asset_book: AssetBook


def __dummy__():
    from anre.config.config import config as anre_config
    from anre.utils.Json.Json import Json

    _file_path = anre_config.path.get_path_to_root_dir(
        'src/anre/connection/polymarket/api/cache/tests/resources/info_step_list.json'
    )
    info_step_list = Json.load(path=_file_path)

    clob_market_info_dict = info_step_list[0]['clob_market_info_dict']

    ### zero step
    clob_mob_list = info_step_list[0]['clob_mob_list']
    clob_public_mob_0_cache = PublicMarketBook.new_from_clob_market_info_dict(
        clob_market_info_dict=clob_market_info_dict
    )
    for clob_mob in clob_mob_list:
        clob_public_mob_0_cache.update_from_clob_mob(clob_mob=clob_mob)

    ### first step
    clob_mob_list = info_step_list[1]['clob_mob_list']
    clob_public_mob_1_cache = PublicMarketBook.new_from_clob_market_info_dict(
        clob_market_info_dict=clob_market_info_dict
    )
    for clob_mob in clob_mob_list:
        clob_public_mob_1_cache.update_from_clob_mob(clob_mob=clob_mob)

    ws_market_message_list = info_step_list[1]['ws_market_message_list']
    ws_public_mob_1_cache = PublicMarketBook.new_from_clob_market_info_dict(
        clob_market_info_dict=clob_market_info_dict
    )
    for ws_message in ws_market_message_list:
        ws_public_mob_1_cache.update_from_ws_message(ws_message=ws_message)

    # patikrinam as ws ir clob info sutampa
    assert clob_public_mob_1_cache == ws_public_mob_1_cache

    # ar yes ir no yra revertinti variantai?
    pairs = zip(
        clob_public_mob_1_cache.yes_asset_book.lob1000.bids.items(),
        reversed(clob_public_mob_1_cache.no_asset_book.lob1000.asks.items()),
    )
    for yes_i, no_i in pairs:
        assert yes_i[0] + no_i[0] == 1000
        assert yes_i[1] == no_i[1]

    ###

    info_step_list[3].keys()
    info_step_list[3]['ws_house_message_list']

    public_market_book

    market_order_book = info_step_list[0]['market_order_book']
    market_order_book
