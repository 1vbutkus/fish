import json
import threading
import time

from websocket import WebSocketApp

MARKET_CHANNEL = "market"
USER_CHANNEL = "user"


class WebSocketOrderBook:
    def __init__(self, channel_type, url, data, auth, message_callback, verbose):
        self.channel_type = channel_type
        self.url = url
        self.data = data
        self.auth = auth
        self.message_callback = message_callback
        self.verbose = verbose
        furl = url + "/ws/" + channel_type
        self.ws = WebSocketApp(
            furl,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open,
            on_reconnect=self._on_reconnect,
            on_pong=self._on_pong,
        )
        self.orderbooks = {}

    def _on_message(self, ws, message):
        print(message)
        pass

    def _on_reconnect(self, ws):
        print('_on_reconnect')


    def _on_error(self, ws, error):
        print("---Error---: ", error)


    def _on_close(self, ws, *args):
        print("closing")

    def _on_pong(self, *args):
        print("_on_pong", args)


    def _on_open(self, ws):
        if self.channel_type == MARKET_CHANNEL:
            ws.send(json.dumps({"assets_ids": self.data, "type": MARKET_CHANNEL}))
        elif self.channel_type == USER_CHANNEL and self.auth:
            ws.send(json.dumps({"markets": self.data, "type": USER_CHANNEL, "auth": self.auth}))
        else:
            exit(1)

        ws.send("PING")

    def ping(self, ws):
        while True:
            ws.send("PING")
            time.sleep(10)

    def run(self):
        self.wst = threading.Thread(target=lambda: self.ws.run_forever(reconnect=True, ping_interval=10, ping_timeout=5, ping_payload='PING',))
        self.wst.daemon = True
        self.wst.start()


def __dummy7__():
    from anre.config.config import config as anre_config

    polymarket_creds = anre_config.cred.get_polymarket_creds()

    url = "wss://ws-subscriptions-clob.polymarket.com"
    # Complete these by exporting them from your initialized client.

    # https://polymarket.com/event/what-will-powell-say-during-june-press-conference/will-powell-say-inflation-40-times-during-june-press-conference
    # market = "0xc2c0d4a0500a76186568270e28ff3619e7598578d2e90094bb89f2e0371cff0a"

    asset_ids = [
        "52315409316147689027926869759851918963034723648533663925491006933785120902515",
        "70972590478128483214197564500183134662564307331464794599405195997913245249009",
    ]
    condition_ids = []  # no really need to filter by this one

    auth = {
        'apikey': polymarket_creds['ApiCreds']["key"],
        'secret': polymarket_creds['ApiCreds']["secret"],
        'passphrase': polymarket_creds['ApiCreds']["passphrase"],
    }

    market_connection = WebSocketOrderBook(MARKET_CHANNEL, url, asset_ids, auth, None, True)
    market_connection.run()
    market_connection.ws.send("aaa")
    market_connection.ws.close()
    market_connection.wst.is_alive()
    market_connection.ws.sock.ping("ping")
    market_connection.ws.sock.send("ping")

    # user_connection = WebSocketOrderBook(USER_CHANNEL, url, condition_ids, auth, None, True)

    # market_connection.run()
    # user_connection.run()

    print(market_connection)
    # print(user_connection)
