import time

from anre.config.config import config as anre_config
from anre.connection.polymarket.api.clob import ClobClient
from anre.connection.polymarket.api.data import DataClient
from anre.connection.polymarket.api.websocket.websocket import PolymarketWebSocket
from anre.utils.Json.Json import Json


def run_book_steps_and_save_to_file(overwrite: bool = False):
    condition_id = '0xae546fe6f033bb5f9f7904bff4dbb142659953229c458ec0d0726d4c0c32f65f'  # condition_id = '0xae546fe6f033bb5f9f7904bff4dbb142659953229c458ec0d0726d4c0c32f65f'
    clob_client = ClobClient()

    clob_market_info_dict = clob_client.get_market_info(condition_id=condition_id)
    asset_ids = [el['token_id'] for el in clob_market_info_dict['tokens']]
    asset_id, counter_asser_id = asset_ids

    ### isalomisus ordersiu,kad nemaisytu
    clob_client.cancel_orders_by_market(condition_id=condition_id)
    time.sleep(1)
    clob_house_order_list_0 = clob_client.get_house_orders(condition_id=condition_id)
    assert len(clob_house_order_list_0) == 0

    # imam nulini stata
    clob_mob_list_0 = clob_client.get_mob_list(token_ids=asset_ids)

    # get best prices
    mob_dict = [mb for mb in clob_mob_list_0 if mb['asset_id'] == asset_id][0]
    assert mob_dict['asset_id'] == asset_id
    bid1000 = int(1000 * max([float(el['price']) for el in mob_dict['bids']]))
    ask1000 = int(1000 * min([float(el['price']) for el in mob_dict['asks']]))
    assert bid1000 >= 40
    assert ask1000 <= 960

    limit_price = (bid1000 - 20) / 1000
    place_resp = clob_client.place_order(
        token_id=asset_id,
        price=limit_price,
        size=20,
        side="BUY",
    )
    assert place_resp['success'] is True
    assert place_resp['status'] == 'live'
    time.sleep(5)

    clob_client.get_house_orders(asset_id=asset_id)
    clob_client.get_house_orders(asset_id=counter_asser_id)

    # pasimam pradini statusa(su egzistuojanciu orderiu)
    clob_mob_list_1 = clob_client.get_mob_list(token_ids=asset_ids)
    clob_house_order_list_1 = clob_client.get_house_orders(condition_id=condition_id)

    # startuojam streamus
    market_ws = PolymarketWebSocket.new_markets(asset_ids=asset_ids)
    market_ws.start()
    house_ws = PolymarketWebSocket.new_house_orders(condition_ids=[condition_id])
    house_ws.start()

    time.sleep(1)
    ws_market_message_list_1 = market_ws.messenger.get_peek_messages()
    ws_house_message_list_1 = house_ws.messenger.get_peek_messages()

    # sukuriam dar du orderius
    place_resp = clob_client.place_order(
        token_id=asset_id,
        price=limit_price,
        size=22,
        side="BUY",
    )
    assert place_resp['success'] is True
    assert place_resp['status'] == 'live'

    place_resp = clob_client.place_order(
        token_id=asset_id,
        price=limit_price - 0.01,
        size=25,
        side="BUY",
    )
    assert place_resp['success'] is True
    assert place_resp['status'] == 'live'

    # sukuriam orderi kitoje pusee:
    limit_price = (1000 - ask1000 - 20) / 1000
    place_resp = clob_client.place_order(
        token_id=counter_asser_id,
        price=limit_price,
        size=27,
        side="BUY",
    )
    assert place_resp['success'] is True
    assert place_resp['status'] == 'live'

    time.sleep(5)

    # pasiimam nuotrauka
    clob_mob_list_2 = clob_client.get_mob_list(token_ids=asset_ids)
    clob_house_order_list_2 = clob_client.get_house_orders(condition_id=condition_id)
    ws_market_message_list_2 = market_ws.messenger.get_peek_messages()
    ws_house_message_list_2 = house_ws.messenger.get_peek_messages()

    # cancel orders
    clob_client.cancel_orders_by_market(condition_id=condition_id)
    time.sleep(5)
    _house_orders = clob_client.get_house_orders(condition_id=condition_id)
    assert len(_house_orders) == 0

    # pasiimam nuotrauka
    clob_mob_list_3 = clob_client.get_mob_list(token_ids=asset_ids)
    clob_house_order_list_3 = clob_client.get_house_orders(condition_id=condition_id)
    ws_market_message_list_3 = market_ws.messenger.get_peek_messages()
    ws_house_message_list_3 = house_ws.messenger.get_peek_messages()

    book_change_step_list = [
        {
            'clob_market_info_dict': clob_market_info_dict,
            'clob_mob_list': clob_mob_list_0,
            'clob_house_order_list': clob_house_order_list_0,
            'ws_market_message_list': [],
            'ws_house_message_list': [],
        },
        {
            'clob_mob_list': clob_mob_list_1,
            'clob_house_order_list': clob_house_order_list_1,
            'ws_market_message_list': ws_market_message_list_1,
            'ws_house_message_list': ws_house_message_list_1,
        },
        {
            'clob_mob_list': clob_mob_list_2,
            'clob_house_order_list': clob_house_order_list_2,
            'ws_market_message_list': ws_market_message_list_2,
            'ws_house_message_list': ws_house_message_list_2,
        },
        {
            'clob_mob_list': clob_mob_list_3,
            'clob_house_order_list': clob_house_order_list_3,
            'ws_market_message_list': ws_market_message_list_3,
            'ws_house_message_list': ws_house_message_list_3,
        },
    ]

    _file_path = anre_config.path.get_path_to_root_dir(
        'src/anre/connection/polymarket/api/cache/tests/resources/book_change_step_list.json'
    )
    Json.dump(book_change_step_list, path=_file_path, overwrite=True, useIndent=True)


def run_trade_steps_and_save_to_file(overwrite: bool = False):
    condition_id = '0xae546fe6f033bb5f9f7904bff4dbb142659953229c458ec0d0726d4c0c32f65f'  # condition_id = '0xae546fe6f033bb5f9f7904bff4dbb142659953229c458ec0d0726d4c0c32f65f'
    clob_client = ClobClient()
    data_client = DataClient()

    clob_market_info_dict = clob_client.get_market_info(condition_id=condition_id)
    asset_ids = [el['token_id'] for el in clob_market_info_dict['tokens']]
    asset_id, counter_asser_id = asset_ids

    # imam nulini stata
    clob_mob_list_0 = clob_client.get_mob_list(token_ids=asset_ids)

    # get best prices
    mob_dict = [mb for mb in clob_mob_list_0 if mb['asset_id'] == asset_id][0]
    assert mob_dict['asset_id'] == asset_id
    bid1000 = int(1000 * max([float(el['price']) for el in mob_dict['bids']]))
    ask1000 = int(1000 * min([float(el['price']) for el in mob_dict['asks']]))
    assert bid1000 >= 40
    assert ask1000 <= 960

    # nuotrauka
    position_list_0 = data_client.get_house_position_dict_list(condition_id=condition_id)
    assert len(position_list_0) == 2
    data_trade_list_0 = data_client.get_house_trade_dict_list(condition_id=condition_id, limit=100)
    assert len(data_trade_list_0) < 100
    clob_trade_list_0 = clob_client.get_house_trade_dict_list(condition_id=condition_id)
    assert len(clob_trade_list_0) < 100

    # startuojam streamus
    market_ws = PolymarketWebSocket.new_markets(asset_ids=asset_ids)
    market_ws.start()
    house_ws = PolymarketWebSocket.new_house_orders(condition_ids=[condition_id])
    house_ws.start()
    time.sleep(1)
    ws_market_message_list_0 = market_ws.messenger.get_peek_messages()
    ws_house_message_list_0 = house_ws.messenger.get_peek_messages()

    # perkam
    place_place_resp_1 = clob_client.place_order(
        token_id=asset_id,
        price=0.07,
        size=33,
        side='BUY',
    )
    time.sleep(30)
    order_get_resp_1 = clob_client.get_house_order(order_id=place_place_resp_1['orderID'])

    # nuotrauka
    position_list_1 = data_client.get_house_position_dict_list(condition_id=condition_id)
    data_trade_list_1 = data_client.get_house_trade_dict_list(condition_id=condition_id, limit=100)
    clob_trade_list_1 = clob_client.get_house_trade_dict_list(condition_id=condition_id)
    ws_market_message_list_1 = market_ws.messenger.get_peek_messages()
    ws_house_message_list_1 = house_ws.messenger.get_peek_messages()

    # parduodam
    place_place_resp_2 = clob_client.place_order(
        token_id=asset_id,
        price=0.03,
        size=33,
        side='SELL',
    )
    time.sleep(30)
    order_get_resp_2 = clob_client.get_house_order(order_id=place_place_resp_1['orderID'])

    # nuotrauka
    position_list_2 = data_client.get_house_position_dict_list(condition_id=condition_id)
    data_trade_list_2 = data_client.get_house_trade_dict_list(condition_id=condition_id, limit=100)
    clob_trade_list_2 = clob_client.get_house_trade_dict_list(condition_id=condition_id)
    ws_market_message_list_2 = market_ws.messenger.get_peek_messages()
    ws_house_message_list_2 = house_ws.messenger.get_peek_messages()

    # clean up
    clob_client.cancel_orders_by_market(condition_id=condition_id)

    book_change_step_list = [
        {
            'clob_market_info_dict': clob_market_info_dict,
            'clob_mob_list': clob_mob_list_0,
            'position_list': position_list_0,
            'data_trade_list': data_trade_list_0,
            'clob_trade_list': clob_trade_list_0,
            'ws_market_message_list': ws_market_message_list_0,
            'ws_house_message_list': ws_house_message_list_0,
        },
        {
            'position_list': position_list_1,
            'data_trade_list': data_trade_list_1,
            'clob_trade_list': clob_trade_list_1,
            'place_place_resp': place_place_resp_1,
            'order_get_resp': order_get_resp_1,
            'ws_market_message_list': ws_market_message_list_1,
            'ws_house_message_list': ws_house_message_list_1,
        },
        {
            'position_list': position_list_2,
            'data_trade_list': data_trade_list_2,
            'clob_trade_list': clob_trade_list_2,
            'place_place_resp': place_place_resp_2,
            'order_get_resp': order_get_resp_2,
            'ws_market_message_list': ws_market_message_list_2,
            'ws_house_message_list': ws_house_message_list_2,
        },
    ]

    _file_path = anre_config.path.get_path_to_root_dir(
        'src/anre/connection/polymarket/api/cache/tests/resources/trade_change_step_list.json'
    )
    Json.dump(book_change_step_list, path=_file_path, overwrite=True, useIndent=True)


if __name__ == '__main__':
    pass
    # run_book_steps_and_save_to_file(overwrite=True)
    # run_trade_steps_and_save_to_file(overwrite=True)
