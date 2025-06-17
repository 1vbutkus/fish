from anre.connection.polymarket.api.clob import BUY, ClobClient
from anre.utils import testutil


class TestClobApi(testutil.TestCase):
    @testutil.api
    def test_smoke(self) -> None:
        client = ClobClient()

        next_cursor = ClobClient.number_to_cursor(57050)
        markets_chunk = client.get_markets_chunk(next_cursor=next_cursor)
        assert markets_chunk
        markets_chunk = client.get_simplified_markets_chunk(next_cursor=next_cursor)
        assert markets_chunk
        markets_chunk = client.get_sampling_markets_chunk(next_cursor='')
        assert markets_chunk
        markets_chunk = client.get_sampling_simplified_markets_chunk(next_cursor='')
        assert markets_chunk

        market_dict = None
        for _market in markets_chunk['data']:
            price = _market['tokens'][0]['price']
            if _market['active'] and _market['accepting_orders'] and price > 0.1 and price < 0.9:
                market_dict = _market
                break
        assert market_dict

        condition_id = market_dict['condition_id']
        token_dict = market_dict['tokens'][0]
        token_id = token_dict['token_id']

        price_history = client.get_price_history(token_id=token_id, interval='1m', fidelity=10)
        assert price_history
        order_book = client.get_market_order_book(token_id=token_id)
        assert order_book

        ### orders

        orders_chunk = client.get_house_orders_chunk(condition_id=condition_id)
        old_count = orders_chunk['count']
        place_resp = client.place_order(
            token_id=token_id,
            price=0.05,
            size=10,
            side=BUY,
        )
        order = client.get_house_order(order_id=place_resp['orderID'])
        orders_chunk = client.get_house_orders_chunk(condition_id=condition_id)
        assert orders_chunk['count'] == old_count + 1

        order_list = client.get_house_orders(condition_id=condition_id)
        assert order_list

        # client.cancel_market_orders(condition_id=condition_id)
        client.cancel_orders_by_id(order_ids=[order['id']])
        orders_chunk = client.get_house_orders_chunk(condition_id=condition_id)
        assert orders_chunk['count'] == old_count

        house_positions = client.get_house_positions()
        assert isinstance(house_positions, list)
