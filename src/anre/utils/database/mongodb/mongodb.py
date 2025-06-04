# mypy: disable-error-code="assignment,call-arg,union-attr,var-annotated"
import pymongo
from pymongo.collection import Collection
from pymongo.database import Database


class Mongodb:
    def __init__(self, conStr: str, dbName: str) -> None:
        self.conStr = conStr
        self.dbName = dbName

        self._client: pymongo.MongoClient | None = None
        self._db: Database | None = None

    def __del__(self):
        if self._client is not None:
            self._client.close()

        self._client = None
        self._db = None

    @property
    def client(self) -> pymongo.MongoClient:
        if self._client is None:
            try:
                client = pymongo.MongoClient(self.conStr, serverSelectionTimeoutMS=5000)
                client.server_info()
            except pymongo.errors.ServerSelectionTimeoutError:
                print('Failed to connect')
                raise

            self._client = client

        return self._client

    @property
    def db(self) -> Database:
        if self._db is None:
            self._db = self.client[self.dbName]

        return self._db

    def showCl(self, cl: Collection | str, n=3):
        """Greitas collection pasiziureijmas (pandas_ print analogas)"""

        if isinstance(cl, str):
            cl = self.db[cl]

        print("\n")
        count = cl.estimated_document_count()
        if count > n * 2:
            res = cl.find(
                projection={'_id': False},
                sort=[
                    (
                        '$natural',
                        1,
                    )
                ],
                limit=n,
            )
            for r in res:
                print(r)
                print("-----")
            print("...")
            res = cl.find(
                projection={'_id': False},
                sort=[
                    (
                        '$natural',
                        -1,
                    )
                ],
                limit=n,
            )
            rList = []
            for r in res:
                rList.append(r)
            rList.reverse()
            for r in rList:
                print("-----")
                print(r)
        else:
            res = cl.find(
                projection={'_id': False},
                sort=[
                    (
                        '$natural',
                        1,
                    )
                ],
            )
            for r in res:
                print(r)

        print('\nCount:{}'.format(count))

    def insert(self, clName, recs, ordered: bool = False):
        """Insert standartinis apvalkalas

        Protingesnem uzklausos reikes patiems knistis
        """

        if len(recs) == 0:
            return None

        cl = self.db[clName]
        result = cl.insert_many(documents=recs, ordered=ordered)
        return result

    @staticmethod
    def ensure_index(cl: Collection, name: str, keys: list, **kwargs):
        """Uztikrina, kad atitinkmas indeksas egzistuotu"""
        try:
            isIndex = name in cl.index_information().keys()
        except Exception:
            isIndex = False
        if not isIndex:
            cl.create_index(keys=keys, name=name, **kwargs)
