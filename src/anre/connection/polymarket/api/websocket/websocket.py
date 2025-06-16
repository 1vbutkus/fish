import json
import logging
import threading
import time
from typing import Optional, Tuple

import orjson
from websocket import WebSocketApp, WebSocketException

from anre.config.config import config as anre_config
from anre.connection.polymarket.api.websocket.messenger import Messenger

MARKET_CHANNEL = 'market'
USER_CHANNEL = 'user'

_channel_uri_map = {
    MARKET_CHANNEL: "/ws/market",
    USER_CHANNEL: "/ws/user",
}


# TODO:
# Paasirodo gali buti avejai, kada ping zinutesvaiksto,bet messagaineateina. Tuomet negalimekokybiškai atskirti connectionlosonuozinuciunebuvimo
# Turbut tiesiogreikestureti QA,kuris gal ir testorderiideda. Irsiapsnapsotuspaziuri.
# Jei aisku, kad neiasku, tai reikia kazkaip siusti lock signala. Ir ji pakelti, kai atsistato.
#


class PolymarketWebSocket:
    _url = "wss://ws-subscriptions-clob.polymarket.com"

    @classmethod
    def new_markets(cls, asset_ids: list[str], messenger: Messenger = None):
        if messenger is None:
            messenger = Messenger()
        self = cls(messenger=messenger, channel_type='market', subscribe_items=asset_ids)
        return self

    @classmethod
    def new_house_orders(cls, condition_ids: list[str]=None, messenger: Messenger = None):
        if messenger is None:
            messenger = Messenger()
        if condition_ids is None:
            condition_ids = []
        self = cls(messenger=messenger, channel_type='user', subscribe_items=condition_ids)
        return self

    def __init__(self, messenger: Messenger, channel_type: str, subscribe_items: list[str] | None = None):
        subscribe_items = [] if subscribe_items is None else subscribe_items
        assert isinstance(subscribe_items, (list, tuple))

        assert channel_type in _channel_uri_map, (
            f"channel_type must be one of {_channel_uri_map.keys()}"
        )
        if channel_type == MARKET_CHANNEL:
            assert subscribe_items, (
                f"subscribe_items must be non-empty for market channel, got {subscribe_items}"
            )

        polymarket_creds = anre_config.cred.get_polymarket_creds()
        self._auth = {
            'apikey': polymarket_creds['ApiCreds']["key"],
            'secret': polymarket_creds['ApiCreds']["secret"],
            'passphrase': polymarket_creds['ApiCreds']["passphrase"],
        }

        self.channel_type = channel_type
        self.subscribe_items = subscribe_items
        self._logger = logging.getLogger(__name__)
        self._pong_event = threading.Event()
        self._qa_event = threading.Event()
        self._last_receive_time = float(0)
        self._ping_interval = 10
        self._ws: Optional[WebSocketApp] = None
        self._messanger = messenger

        assert self._ping_interval > 5

    def __del__(self):
        self.stop()

    @property
    def messenger(self)->Messenger:
        return self._messanger

    def _new_ws(self) -> WebSocketApp:
        furl = self._url + _channel_uri_map[self.channel_type]
        ws = WebSocketApp(
            furl,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open,
            on_reconnect=self._on_reconnect,
            on_pong=self._on_ws_pong,
        )
        return ws

    def _proc_message(self, message: dict):
        assert isinstance(message, dict)
        assert 'event_type' in message
        self._messanger.put(message)

    def _on_message(self, ws, message):
        self._last_receive_time = receive_time = time.time()
        if message == 'PONG':
            self._pong_event.set()
            self._logger.debug("pong")
        else:
            parsed_message = orjson.loads(message)
            assert isinstance(parsed_message, list)
            self._last_receive_time = receive_time
            for submessage in parsed_message:
                submessage['_rt'] = receive_time
                self._proc_message(submessage)

    def _on_reconnect(self, ws):
        print('_on_reconnect')
        message = {'event_type': '_internal', 'event': 'reconnect', 'timestamp': time.time()}
        self._proc_message(message)
        self._send_subscribe()

    def _on_error(self, ws, error):
        message = {
            'event_type': '_internal',
            'event': 'error',
            'error': error,
            'timestamp': time.time(),
        }
        self._proc_message(message)

    def _on_close(self, ws, *args):
        message = {'event_type': '_internal', 'event': 'close', 'timestamp': time.time()}
        self._proc_message(message)

    def _on_ws_pong(self, ws, *args):
        """WS have internal pinging thread. It helps to keep connection alive. But if it passes, it does not mean that the messages are comming.

        Gad uztikrinti ar zinutes eina, dar nusiunciam pinga, ir ziurim kiek laiko praejo nuo paskutines zinutes.
        """
        ws.send("PING")
        if time.time() - self._last_receive_time > self._ping_interval * 3:
            msg = "Connection error. Messages are not coming. We will try to reconnect."
            self._logger.warning(msg)
            self._connect(reconnect=True)

    def _on_open(self, ws):
        message = {'event_type': '_internal', 'event': 'open', 'timestamp': time.time()}
        self._proc_message(message)
        self._send_subscribe()
        ws.send("PING")

    def _connect(self, reconnect: bool = False):
        if self._ws is not None:
            if reconnect:
                self._ws.close()
                self._ws = None
            else:
                raise RuntimeError(
                    f"already connected. Use reconnect=True if needed. url: {self._ws.url}"
                )

        if self._ws is None:
            self._ws = self._new_ws()

        self.wst = threading.Thread(
            target=lambda: self._ws.run_forever(
                reconnect=2, ping_interval=self._ping_interval, ping_timeout=self._ping_interval - 2
            )
        )
        self.wst.daemon = True
        self.wst.start()

        # Wait for connect before continuing
        conn_timeout = 5
        while ((not self._ws.sock) or (not self._ws.sock.connected)) and conn_timeout > 0:
            time.sleep(1)
            conn_timeout -= 1

        if conn_timeout <= 0:
            self._logger.error("Couldn't connect to WS! Exiting.")
            self.stop()
            raise WebSocketException('Couldn\'t connect to WS! Exiting.')

    def start(self):
        self._connect(reconnect=False)

    def stop(self):
        if self._ws:
            self._ws.close()

    def _send_subscribe(self):
        if self.channel_type == MARKET_CHANNEL:
            self._ws.send(json.dumps({"assets_ids": self.subscribe_items, "type": MARKET_CHANNEL}))
        elif self.channel_type == USER_CHANNEL:
            assert self._auth
            self._ws.send(
                json.dumps({
                    "markets": self.subscribe_items,
                    "type": USER_CHANNEL,
                    "auth": self._auth,
                })
            )
        else:
            raise NotImplementedError()

    def resubscribe(self, subscribe_items: list[str]):
        self.subscribe_items = subscribe_items
        self._connect(reconnect=True)

    def ping(self, timeout=5) -> Tuple[bool, float]:
        if self._ws is None:
            return False, float(0)

        try:
            self._pong_event.clear()
            sent_ping_time = time.time()
            self._ws.send("PING")
            res = self._pong_event.wait(timeout=timeout)
            takes_time = time.time() - sent_ping_time
            return res, takes_time
        except:
            return False, 0


def __dummy7__():
    # subscribe_items = [
    #     "52315409316147689027926869759851918963034723648533663925491006933785120902515",
    #     "70972590478128483214197564500183134662564307331464794599405195997913245249009",
    # ]
    subscribe_items = [
        '3796961984592683047724333059166286679049912327822267416870816733710637507501',
        '49752777464497901629052143796178209174998482502782303100115062016623520813466',
        '4035065291772644731876334741178162861113899806117080318351467946714817079716',
        '8807253522691129263460582179245445512612974167513689659640198687172344193269',
        '78397765613055343660981684625548247730988640449758076460513963030464624568339',
        '32991671287341934767805431457746630433481642330962899566829019629930387398671',
        '682015221774154132828847491425153593161189919561460311334386393221845282492',
        '101758403201828059680344010352051946087295880602352642560427952395417662391270',
        '10772588031551349729289948290557133829937274723962850186274243477468724950221',
        '60288428339855018308474917074028475599916506717424294063185522071817526231885',
        '40074888323826266635337686983557595946596117588836086534010374700456164206544',
        '75136810582011998509242990027763463413525994485000954948594930992360574099962',
        '112317011402266313285385277588643241746891964489709475346255125329717458492650',
        '7895405310433215018143712021310484829790209954219231386165007891572254181133',
        '79895334177955799459104165363176942891833635901276798957927316841634035554793',
        '67875176939307751491735562611070904231511991937702186803972237380494079519328',
        '33483037127912259970535820828279013745748448609963942365026052374974935805211',
        '84691356691030809317762076558733279411769621725807832017200558477351459890429',
        '60487116984468020978247225474488676749601001829886755968952521846780452448915',
        '81104637750588840860328515305303028259865221573278091453716127842023614249200',
    ]

    messenger = Messenger()
    self = polymarket_web_socket = PolymarketWebSocket(messenger=messenger, channel_type='market', subscribe_items=subscribe_items)
    polymarket_web_socket.start()
    # polymarket_web_socket.stop()
    polymarket_web_socket.ping()
    polymarket_web_socket._connect(reconnect=True)

    ###### orders
    messages = messenger.get_peek_messages()
    self = polymarket_web_socket = PolymarketWebSocket(messenger=messenger, channel_type='user', subscribe_items=[])
    polymarket_web_socket.start()
    # polymarket_web_socket.stop()
    polymarket_web_socket.ping()



