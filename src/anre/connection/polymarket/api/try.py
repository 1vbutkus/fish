
from anre.connection.polymarket.api.clob import ClobClient
from anre.connection.polymarket.api.websocket.messenger import Messenger
from anre.connection.polymarket.api.websocket.websocket import PolymarketWebSocket
from anre.connection.polymarket.api.cache import MarketBook

def __dummy__():

    condition_id = '0xae546fe6f033bb5f9f7904bff4dbb142659953229c458ec0d0726d4c0c32f65f'  #     condition_id = '0xae546fe6f033bb5f9f7904bff4dbb142659953229c458ec0d0726d4c0c32f65f'
    # condition_id = '0xee3898d16e04818aa853e39e1533b368ad57ca092ec0e6298ccdf41b62786ab9'  # What price will gold close at in 2025?

    clob_client = ClobClient()
    market_dict = clob_client.get_market_info(condition_id=condition_id)
    asset_ids = [el['token_id'] for el in market_dict['tokens']]

    order_books = clob_client.get_order_books(token_ids=asset_ids)
    order_list = clob_client.get_orders(condition_id=condition_id)
    clob_client.cancel_all()


    public_market_messenger = Messenger()
    market_ws = PolymarketWebSocket.new_markets(messenger=public_market_messenger, asset_ids=asset_ids)
    market_ws.start()

    private_order_messenger = Messenger()
    order_ws = PolymarketWebSocket.new_house_orders(messenger=private_order_messenger, condition_ids=[condition_id])
    order_ws.start()


    gross_market_book = MarketBook(
        asset_id=asset_ids[0],
    )
    self = private_order_book = MarketBook(
        asset_id=asset_ids[0],
    )
    order_list





    public_market_messages = public_market_messenger.get_peek_messages()
    private_order_messages = private_order_messenger.get_peek_messages()

    for message in public_market_messages:
        if message.get('asset_id', '') == gross_market_book.asset_id:
            gross_market_book.update_from_public_market_message(message=message)



    private_order_messages



    market_book.update_from_public_market_message(message=public_market_messenger.get_peek_messages()[0])




    market_messenger.get_peek_messages()[:5]

    messages_a = market_messenger.get_peek_messages()
    messages_b = market_messenger.get_peek_messages()

    messages_b[-3:]












    #
    # message = messages[1]
    # self = MarketBook.parse_market_book(message)
    #
    # for message in messages:
    #     if message['event_type'] == 'price_change':
    #         if message['asset_id'] == self.asset_id:
    #             break
    #
    # self.update(message)
    #
    # ####### ORDERS
    #
    # from anre.connection.polymarket.api.clob import BUY, ClobClient
    #
    # ClobClient().get_orders_chunk()
    #
    #
    # messenger = Messenger()
    # self = polymarket_web_socket = PolymarketWebSocket(messenger=messenger, channel_type='user', subscribe_items=[])
    # polymarket_web_socket.start()
    # # polymarket_web_socket.stop()
    # polymarket_web_socket.ping()
    #
    # messages = messenger.get_peek_messages()






