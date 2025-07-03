from dataclasses import dataclass, field

from anre.connection.polymarket.api.cache.base import AssetBook as BaseAssetBook
from anre.connection.polymarket.api.cache.base import Book1000
from anre.connection.polymarket.api.cache.base import BoolMarketOrderBook as BaseMarketOrderBook


@dataclass(frozen=False, repr=False)
class PublicAssetBook(BaseAssetBook):
    asset_id: str
    book1000: Book1000 = field(default_factory=Book1000)
    timestamp: float = float(0)
    hash: str = ''

    def update_from_clob_message(self, message: dict):
        assert 'event_type' not in message
        assert message['asset_id'] == self.asset_id, (
            f'message is not for this asset_id. Expected: {self.asset_id}, got: {message["asset_id"]}'
        )
        timestamp = float(message['timestamp'])
        assert timestamp > self.timestamp, (
            f'update message is not newer. Last update: {self.timestamp}, new update: {timestamp}'
        )
        book1000 = Book1000.new_from_native_prices(asks=message['asks'], bids=message['bids'])
        self.book1000 = book1000
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
            book1000 = Book1000.new_from_native_prices(asks=message['asks'], bids=message['bids'])
            self.book1000 = book1000
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
                self.book1000.update_overwrite(
                    price=float(change['price']), size=float(change['size']), side=change['side']
                )

            self.hash = message['hash']
            self.timestamp = timestamp

        else:
            raise ValueError(f'unknown event type: {event_type}')


@dataclass(frozen=False, repr=False)
class PublicMarketOrderBookCache(BaseMarketOrderBook):
    condition_id: str
    main_asset_book: PublicAssetBook
    counter_asset_book: PublicAssetBook

    def __post_init__(self):
        assert self.main_asset_book.asset_id != self.counter_asset_book.asset_id, (
            f'main_asset_book and counter_asset_book must be different. Got: {self.main_asset_book.asset_id} and {self.counter_asset_book.asset_id}'
        )

    @classmethod
    def new_init(
        cls, condition_id: str, main_asset_id: str, counter_asset_id: str
    ) -> 'PublicMarketOrderBookCache':
        main_asset_book = PublicAssetBook(asset_id=main_asset_id)
        counter_asset_book = PublicAssetBook(asset_id=counter_asset_id)
        return cls(
            condition_id=condition_id,
            main_asset_book=main_asset_book,
            counter_asset_book=counter_asset_book,
        )

    def update_from_clob_mob_list(self, clob_mob_list: list[dict], validate: bool = True):
        for clob_mob in clob_mob_list:
            self._update_from_clob_mob(clob_mob=clob_mob)
        if validate:
            self.validate()

    def update_from_ws_message_list(self, ws_message_list: list[dict], validate: bool = True):
        for ws_message in ws_message_list:
            self._update_from_ws_message(ws_message=ws_message)
        if validate:
            self.validate()

    def _update_from_clob_mob(self, clob_mob: dict):
        assert 'event_type' not in clob_mob
        assert clob_mob['market'] == self.condition_id, (
            f'message is not for this condition_id. Expected: {self.condition_id}, got: {clob_mob["condition_id"]}'
        )
        if clob_mob['asset_id'] == self.main_asset_book.asset_id:
            self.main_asset_book.update_from_clob_message(message=clob_mob)
        elif clob_mob['asset_id'] == self.counter_asset_book.asset_id:
            self.counter_asset_book.update_from_clob_message(message=clob_mob)
        else:
            raise ValueError(f'unknown asset_id: {clob_mob["asset_id"]}')

    def _update_from_ws_message(self, ws_message: dict):
        assert 'event_type' in ws_message, (
            f'message does not have `event_type`. It is not stream message: {ws_message}'
        )
        event_type = ws_message['event_type']
        if event_type in ['book', 'price_change']:
            assert ws_message['market'] == self.condition_id, (
                f'message is not for this condition_id. Expected: {self.condition_id}, got: {ws_message["condition_id"]}'
            )
            if ws_message['asset_id'] == self.main_asset_book.asset_id:
                self.main_asset_book.update_from_ws_message(message=ws_message)
            elif ws_message['asset_id'] == self.counter_asset_book.asset_id:
                self.counter_asset_book.update_from_ws_message(message=ws_message)
            else:
                raise ValueError(f'unknown asset_id: {ws_message["asset_id"]}')

        elif event_type == '_internal':
            pass

        elif event_type == 'tick_size_change':
            pass

        else:
            raise ValueError(f'unknown event type: {event_type}')
