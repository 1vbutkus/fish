import pymongo
from pymongo.errors import BulkWriteError

from anre.utils.database.mongodb.old.dDict import DDict as DDict


class Mongodb:
    def __init__(self, conStr: str, dbName: str) -> None:
        self.conStr = conStr
        self.dbName = dbName

        self._client = None
        self._db = None

    def __del__(self):
        if self._client is not None:
            self._client.close()

        self._client = None
        self._db = None

    @property
    def client(self):
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
    def db(self):
        if self._db is None:
            self._db = self.client[self.dbName]

        return self._db

    ###########################################################################

    def showCl(self, cl, n=3):
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

    def update(self, clName, recs, ids, unset=None, ordered: bool = False):
        """Update standartinis apvalkalas

        Protingesnem uzklausos reikes patiems knistis

        Args:
            ids: list of fiels that identifies record
            unset: list of fiels to unset
            ordered: logical, if an ordered bulk operation should be used
        """

        cl = self.db[clName]

        if ordered:
            bulk = cl.initialize_ordered_bulk_op()
        else:
            bulk = cl.initialize_unordered_bulk_op()

        if unset is None:
            for rec in recs:
                key = DDict.subset_obj(rec, ids=ids)
                bulk.find(key).update({'$set': rec})
        else:
            unsetQQ = {key: '' for key in unset}
            for rec in recs:
                key = DDict.subset_obj(rec, ids=ids)
                bulk.find(key).update({'$set': rec, '$unset': unsetQQ})

        try:
            result = bulk.execute()
            return result
        except BulkWriteError as bwe:
            print(bwe.details)

    def insert(self, clName, recs, ordered: bool = False):
        """Insert standartinis apvalkalas

        Protingesnem uzklausos reikes patiems knistis
        """

        if len(recs) == 0:
            return None

        cl = self.db[clName]
        result = cl.insert_many(documents=recs, ordered=ordered)
        return result

    def insertOnDuplicateUpdate(self, clName, recs, ids, ordered: bool = False):
        """sql insert on duplicate update analogas

        Args:
            clName: collection'o pavadinimas
            recs: list of records
            ids: list, laukai, kurie apibrezia unikaluma
            ordered: logifal. If ordered bulk should be applied.

        Note: Saugiai galima taikyti tik tada, kai istiesu yra sukurtas unikalus indesas. Si funkcija netikrina ar yra toks indekas.

        Returns: bulk summary if all OK, and None on error
        """

        if len(recs) == 0:
            return None

        cl = self.db[clName]

        if ordered:
            bulk = cl.initialize_ordered_bulk_op()
        else:
            bulk = cl.initialize_unordered_bulk_op()

        for rec in recs:
            key = DDict.subset_obj(rec, ids=ids)
            bulk.find(key).upsert().update({'$set': rec})

        try:
            result = bulk.execute()
            return result
        except BulkWriteError as bwe:
            print(bwe.details)

    def insertOnDuplicateUpdate2(self, clName, recs, ids):
        """Letesnis analogas kreipianti kiekviena karta"""

        cl = self.db[clName]

        for rec in recs:
            key = DDict.subset_obj(rec, ids=ids)
            cl.update_one(key, {'$set': rec}, upsert=True)

    def insertOnDuplicateUpdate_conditinal(
        self, clName, recs, ids, upFields, ordered: bool = False
    ):
        """sql insert on duplicate update analogas

        Bet dabar su salygu atskirimu ka irasineti, o ka updatinti.
        Jei reikia viska irasyti ir updatinti, tai geriau naudoti insertOnDuplicateUpdate funkcija.

        Args:
            clName: collection'o pavadinimas
            recs: list of records
            ids: list, laukai, kurie apibrezia unikaluma


        Note: Saugiai galima taikyti tik tada, kai istiesu yra sukurtas unikalus indesas. Si funkcija netikrina ar yra toks indekas.

        Returns: bulk summary if all OK, and None on error
        """

        if len(recs) == 0:
            return None

        cl = self.db[clName]

        if ordered:
            bulk = cl.initialize_ordered_bulk_op()
        else:
            bulk = cl.initialize_unordered_bulk_op()

        for rec in recs:
            key = DDict.subset_obj(rec, ids=ids)
            upRec = DDict.subset_obj(rec, ids=upFields)
            bulk.find(key).update({'$set': upRec})
            bulk.find(key).upsert().update({'$setOnInsert': rec})

        try:
            result = bulk.execute()
            return result
        except BulkWriteError as bwe:
            print(bwe.details)

    def insertOnDuplicateUpdate_conditinal2(self, clName, recs, ids, upFields):
        """Letesnis analogas kreipianti kiekviena karta"""

        if len(recs) == 0:
            return None

        cl = self.db[clName]

        for rec in recs:
            key = DDict.subset_obj(rec, ids=ids)
            upRec = DDict.subset_obj(rec, ids=upFields)
            cl.update_one(key, {'$set': upRec}, upsert=False)
            cl.update_one(key, {'$setOnInsert': rec}, upsert=True)
