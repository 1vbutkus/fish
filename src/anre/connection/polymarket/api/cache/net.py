from dataclasses import dataclass

from anre.connection.polymarket.api.cache.base import AssetBook
from anre.connection.polymarket.api.cache.base import MarketOrderBook as BaseMarketOrderBook
from anre.connection.polymarket.api.cache.house import HouseOrderBook
from anre.connection.polymarket.api.cache.public import PublicMarketOrderBook


@dataclass
class NetMarketOrderBook(BaseMarketOrderBook):
    condition_id: str
    yes_asset_book: AssetBook
    no_asset_book: AssetBook

    @classmethod
    def new(
        cls,
        public_market_order_book: PublicMarketOrderBook,
        house_order_book: HouseOrderBook,
        validate: bool = True,
    ) -> 'NetMarketOrderBook':
        temp_market_order_book = public_market_order_book.sub(house_order_book, validate=False)
        instance = cls(
            condition_id=temp_market_order_book.condition_id,
            yes_asset_book=temp_market_order_book.yes_asset_book,
            no_asset_book=temp_market_order_book.no_asset_book,
        )
        if validate:
            instance.validate()
        return instance
