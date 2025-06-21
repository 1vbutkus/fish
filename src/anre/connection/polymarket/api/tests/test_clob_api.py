import time

from anre.connection.polymarket.api.clob import ClobClient
from anre.utils import testutil


@testutil.api
class TestClobApi(testutil.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        client = ClobClient()
        cls.client = client

    def test_market_info(self) -> None:
        client = self.client

        cursor = 57050
        market_info_chunk = client.get_market_info_chunk(cursor=cursor)
        assert market_info_chunk
        assert set(market_info_chunk) == {'count', 'data', 'limit', 'next_cursor'}

        market_info_list = client.get_market_info_list(cursor=cursor, chunk_limit=4)
        assert len(market_info_list) == 2000

        condition_id = market_info_list[0]['condition_id']
        market_info = client.get_single_market_info(condition_id=condition_id)
        assert isinstance(market_info, dict)
        assert market_info
        assert market_info == market_info_list[0]

        ### sampling
        market_info_chunk = client.get_sampling_market_info_chunk()
        assert market_info_chunk
        assert set(market_info_chunk) == {'count', 'data', 'limit', 'next_cursor'}
        market_info_list = client.get_sampling_market_info_list()
        assert market_info_list

        # does sampling maches general?
        condition_id = market_info_list[0]['condition_id']
        market_info = client.get_single_market_info(condition_id=condition_id)
        assert isinstance(market_info, dict)
        assert market_info
        assert market_info == market_info_list[0]

    def test_simplified_market_info(self) -> None:
        client = self.client

        cursor = 57050
        simplified_market_info_chunk = client.get_simplified_markets_info_chunk(cursor=cursor)
        assert simplified_market_info_chunk
        assert set(simplified_market_info_chunk) == {'count', 'data', 'limit', 'next_cursor'}

        simplified_market_info_list = client.get_simplified_markets_info_list(
            cursor=cursor, chunk_limit=4
        )
        assert len(simplified_market_info_list) == 2000

        ### sampling
        simplified_market_info_chunk = client.get_sampling_simplified_market_info_chunk()
        assert simplified_market_info_chunk
        assert set(simplified_market_info_chunk) == {'count', 'data', 'limit', 'next_cursor'}
        simplified_markets_info_list = client.get_sampling_simplified_markets_info_list(
            chunk_limit=4
        )
        assert simplified_markets_info_list

    def test_house_trades(self) -> None:
        client = self.client

        house_trade_dict_chunk = client.get_house_trade_dict_chunk()
        assert house_trade_dict_chunk
        assert set(house_trade_dict_chunk) == {'count', 'data', 'limit', 'next_cursor'}

        house_trade_dict_list = client.get_house_trade_dict_list(chunk_limit=2)
        assert isinstance(house_trade_dict_list, list)

        house_trade_rec_dict = client.parse_house_trade_dict_list(
            trade_dict_list=house_trade_dict_list
        )
        assert isinstance(house_trade_rec_dict, dict)
        assert house_trade_rec_dict

    def test_market_deeper_data(self) -> None:
        client = self.client

        simplified_markets_info_list = client.get_sampling_simplified_markets_info_list(
            chunk_limit=1
        )
        token_ids = [
            item['token_id']
            for markets_info in simplified_markets_info_list
            for item in markets_info['tokens']
        ]
        token_ids = token_ids[:10]
        token_id = token_ids[0]

        ### look for market data
        price_history = client.get_price_history(token_id=token_id, interval='1m', fidelity=10)
        assert price_history
        mob = client.get_single_mob(token_id=token_id)
        assert mob
        mob_list = client.get_mob_list(token_ids=token_ids)
        assert mob_list

    def test_smoke_house_orders(self) -> None:
        client = self.client

        simplified_markets_info_list = client.get_sampling_simplified_markets_info_list(
            chunk_limit=1
        )

        # find market that is good enouth to place order
        market_dict = None
        for _market in simplified_markets_info_list:
            price = _market['tokens'][0]['price']
            if _market['active'] and _market['accepting_orders'] and price > 0.1 and price < 0.9:
                market_dict = _market
                break
        assert market_dict

        condition_id = market_dict['condition_id']
        token_dict = market_dict['tokens'][0]
        token_id = token_dict['token_id']

        ### place orders

        order_dict_list = client.get_house_order_dict_list(condition_id=condition_id)
        old_count = len(order_dict_list)
        place_resp = client.place_order(
            token_id=token_id,
            price=0.05,
            size=50,
            side="BUY",
        )
        assert place_resp['success']
        order_dict = client.get_single_house_order_dict(order_id=place_resp['orderID'])
        assert isinstance(order_dict, dict)
        assert order_dict
        assert order_dict['status'] == 'LIVE'
        time.sleep(2)
        order_dict_list = client.get_house_order_dict_list(condition_id=condition_id)
        assert len(order_dict_list) == old_count + 1
        order_id = order_dict['id']

        is_order_scoring = client.is_order_scoring(order_id=order_id)
        assert isinstance(is_order_scoring, bool)

        # client.cancel_orders_by_market(condition_id=condition_id)
        cancel_resp = client.cancel_orders_by_id(order_ids=[order_id])
        assert order_id in cancel_resp['canceled']
        order_dict_list = client.get_house_order_dict_list(condition_id=condition_id)
        assert len(order_dict_list) == old_count
