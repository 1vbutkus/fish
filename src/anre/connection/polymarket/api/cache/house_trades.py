from anre.connection.polymarket.api.clob import ClobClient
from anre.connection.polymarket.api.data import DataClient


def __dummy__():
    clob_client = ClobClient()
    data_client = DataClient()

    clob_client.get_house_trades()
    data_client.get_house_trades()



