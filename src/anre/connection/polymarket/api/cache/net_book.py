from dataclasses import dataclass

from anre.connection.polymarket.api.cache.base import AssetBook
from anre.connection.polymarket.api.cache.base import BoolMarketOrderBook as BaseMarketOrderBook
from anre.connection.polymarket.api.cache.house_book import HouseOrderBookCache
from anre.connection.polymarket.api.cache.public_book import PublicMarketOrderBookCache


@dataclass
class NetBoolMarketOrderBook(BaseMarketOrderBook):
    condition_id: str
    yes_asset_book: AssetBook
    no_asset_book: AssetBook

    @classmethod
    def new(
        cls,
        public_market_order_book: PublicMarketOrderBookCache,
        house_order_book: HouseOrderBookCache,
        validate: bool = True,
    ) -> 'NetBoolMarketOrderBook':
        temp_market_order_book = public_market_order_book.sub(house_order_book, validate=False)
        instance = cls(
            condition_id=temp_market_order_book.condition_id,
            yes_asset_book=temp_market_order_book.yes_asset_book,
            no_asset_book=temp_market_order_book.no_asset_book,
        )
        if validate:
            instance.validate()
        return instance
