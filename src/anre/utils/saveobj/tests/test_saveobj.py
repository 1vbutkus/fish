import _pickle as pickle
import os
import tempfile

import numpy as np
import pandas as pd

from anre.utils import saveobj, testutil
from anre.utils.fileSystem.fileSystem import FileSystem


class TestModFunctions(testutil.TestCase):
    dirPath: str
    df: pd.DataFrame

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        dirPath = tempfile.mkdtemp()
        df = pd.DataFrame(np.random.randn(100, 5), columns=['a', 'b', 'c', 'd', 'e'])
        cls.dirPath = dirPath
        cls.df = df

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        FileSystem.delete_folder(path=cls.dirPath, ignore_errors=True)
        assert not os.path.exists(cls.dirPath), f'Folder still exist: {cls.dirPath}'

    def test_json_dumps(self) -> None:
        obj = {'a': 4, "b": [1, 2, 3]}
        cmpstr = saveobj.dumps(obj)
        obj2 = saveobj.loads(cmpstr)
        self.assertTrue(obj == obj2)

    def test_json_dump_simple(self) -> None:
        dirPath = self.dirPath
        filePath = os.path.join(dirPath, 'data_simple.json')
        obj = {'a': 4, "b": [1, 2, 3]}
        assert not os.path.exists(filePath)
        saveobj.dump(obj=obj, path=filePath)
        assert os.path.exists(filePath)
        obj2 = saveobj.load(path=filePath)
        self.assertTrue(obj == obj2)
        self.assertFalse(obj is obj2)

    def test_json_dump_kwargs(self) -> None:
        dirPath = self.dirPath
        filePath = os.path.join(dirPath, 'data_numpy.json')
        obj = {'a': 4, "b": [1, 2, 3], 'c': np.array([4, 5, 6])}
        assert not os.path.exists(filePath)
        saveobj.dump(obj=obj, path=filePath, useNumpy=True)
        assert os.path.exists(filePath)
        obj2 = saveobj.load(path=filePath)
        objExp = {'a': 4, "b": [1, 2, 3], 'c': [4, 5, 6]}
        self.assertTrue(objExp == obj2)
        self.assertFalse(objExp is obj2)
        self.assertFalse(obj is obj2)

    def test_dumps_df(self) -> None:
        df = self.df
        cmpstr = saveobj.dumps(df)
        df2 = saveobj.loads(cmpstr)
        self.assertTrue(df.equals(df2))

    def test_dump_df(self) -> None:
        df = self.df
        dirPath = self.dirPath

        filePath = os.path.join(dirPath, 'df.pkl')
        saveobj.dump(df, filePath, overwrite=True)
        df2 = saveobj.load(filePath)
        self.assertTrue(df.equals(df2))

        filePath = os.path.join(dirPath, 'df.pkl.gz')
        saveobj.dump(df, filePath, overwrite=True)
        df2 = saveobj.load(filePath)
        self.assertTrue(df.equals(df2))

        filePath = os.path.join(dirPath, 'df.pkl.bz2')
        saveobj.dump(df, filePath, overwrite=True)
        df2 = saveobj.load(filePath)
        self.assertTrue(df.equals(df2))

        filePath = os.path.join(dirPath, 'df.parquet')
        saveobj.dump(df, filePath, overwrite=True)
        df2 = saveobj.load(filePath)
        self.assertTrue(df.equals(df2))
        df2 = pd.read_parquet(filePath)
        self.assertTrue(df.equals(df2))

        filePath = os.path.join(dirPath, 'df.parquet.gz')
        saveobj.dump(df, filePath, overwrite=True, compression='gzip')
        df2 = saveobj.load(filePath)
        self.assertTrue(df.equals(df2))
        df2 = pd.read_parquet(filePath)
        self.assertTrue(df.equals(df2))

    def test_gzipFile(self) -> None:
        df = self.df
        dirPath = self.dirPath

        filePath = os.path.join(dirPath, 'temp.csv')
        df.to_csv(filePath, index=False, sep=',')
        saveobj.gzipFile(filePath, delSource=True)
        df2 = pd.read_csv(filePath + '.gz')
        df.equals(df2)
        self.assertTrue((df - df2).abs().max().max() < 0.000001)

    def test_parquet_with_time(self) -> None:
        dirPath = self.dirPath

        df_bytes = b'\x80\x04\x95H\x06\x00\x00\x00\x00\x00\x00\x8c\x11pandas.core.frame\x94\x8c\tDataFrame\x94\x93\x94)\x81\x94}\x94(\x8c\x04_mgr\x94\x8c\x1epandas.core.internals.managers\x94\x8c\x0cBlockManager\x94\x93\x94(\x8c\x16pandas._libs.internals\x94\x8c\x0f_unpickle_block\x94\x93\x94\x8c\x13pandas._libs.arrays\x94\x8c\x1c__pyx_unpickle_NDArrayBacked\x94\x93\x94\x8c\x1cpandas.core.arrays.datetimes\x94\x8c\rDatetimeArray\x94\x93\x94J\x1f\x06\xf1\x04N\x87\x94R\x94\x8c\x05numpy\x94\x8c\x05dtype\x94\x93\x94\x8c\x02M8\x94\x89\x88\x87\x94R\x94(K\x04\x8c\x01<\x94NNNJ\xff\xff\xff\xffJ\xff\xff\xff\xffK\x00}\x94(C\x02ns\x94K\x01K\x01K\x01t\x94\x86\x94t\x94b\x8c\x16numpy._core.multiarray\x94\x8c\x0c_reconstruct\x94\x93\x94h\x14\x8c\x07ndarray\x94\x93\x94K\x00\x85\x94C\x01b\x94\x87\x94R\x94(K\x01K\x02K\x05\x86\x94h\x16\x8c\x02M8\x94\x89\x88\x87\x94R\x94(K\x04h\x1aNNNJ\xff\xff\xff\xffJ\xff\xff\xff\xffK\x00}\x94(C\x02ns\x94K\x01K\x01K\x01t\x94\x86\x94t\x94b\x89CP\x006\xcc\x89\x93\x86\x05\x18\x80r&|\x94\x86\x05\x18\xc0\xb45|\x94\x86\x05\x18\xc0\xb45|\x94\x86\x05\x18\xc0\xb45|\x94\x86\x05\x18\x006\xcc\x89\x93\x86\x05\x18\x80r&|\x94\x86\x05\x18\xc0\xb45|\x94\x86\x05\x18\xc1\xb45|\x94\x86\x05\x18\xc2\xb45|\x94\x86\x05\x18\x94t\x94b}\x94\x8c\x05_freq\x94Ns\x87\x94b\x8c\x08builtins\x94\x8c\x05slice\x94\x93\x94K\x03K\x0bK\x04\x87\x94R\x94K\x02\x87\x94R\x94h\x0bh\x0eh\x11J\x1f\x06\xf1\x04N\x87\x94R\x94h\x16\x8c\x02M8\x94\x89\x88\x87\x94R\x94(K\x04h\x1aNNNJ\xff\xff\xff\xffJ\xff\xff\xff\xffK\x00}\x94(C\x02us\x94K\x01K\x01K\x01t\x94\x86\x94t\x94bh"h$K\x00\x85\x94h&\x87\x94R\x94(K\x01K\x02K\x05\x86\x94h\x16\x8c\x02M8\x94\x89\x88\x87\x94R\x94(K\x04h\x1aNNNJ\xff\xff\xff\xffJ\xff\xff\xff\xffK\x00}\x94(C\x02us\x94K\x01K\x01K\x01t\x94\x86\x94t\x94b\x89CP\xc0\x1d\xc7PG&\x06\x00x,\x05QG&\x06\x00x,\x05QG&\x06\x00x,\x05QG&\x06\x00x,\x05QG&\x06\x00_&\xc7PG&\x06\x00\xc24\x05QG&\x06\x00\xcd4\x05QG&\x06\x00\xce4\x05QG&\x06\x00\xd04\x05QG&\x06\x00\x94t\x94b}\x94h5Ns\x87\x94bh9K\x01K\x03K\x01\x87\x94R\x94K\x02\x87\x94R\x94h\x0bh"h$K\x00\x85\x94h&\x87\x94R\x94(K\x01K\x03K\x05\x86\x94h\x16\x8c\x02f8\x94\x89\x88\x87\x94R\x94(K\x03h\x1aNNNJ\xff\xff\xff\xffJ\xff\xff\xff\xffK\x00t\x94b\x89Cxo\x12\x83\xc0\xca\x01;@o\x12\x83\xc0\xca\x01;@o\x12\x83\xc0\xca\x01;@o\x12\x83\xc0\xca\x01;@o\x12\x83\xc0\xca\x01;@5^\xbaI\x0c\x02;@\xfc\xa9\xf1\xd2M\x02;@\xc3\xf5(\\\x8f\x02;@\x89A`\xe5\xd0\x02;@P\x8d\x97n\x12\x03;@R\xb8\x1e\x85\xeb\x01;@6^\xbaI\x0c\x02;@\x19\x04V\x0e-\x02;@\xfc\xa9\xf1\xd2M\x02;@\xe0O\x8d\x97n\x02;@\x94t\x94bh9K\x04K\x07K\x01\x87\x94R\x94K\x02\x87\x94R\x94h\x0bh"h$K\x00\x85\x94h&\x87\x94R\x94(K\x01K\x01K\x05\x86\x94h\x16\x8c\x02i8\x94\x89\x88\x87\x94R\x94(K\x03h\x1aNNNJ\xff\xff\xff\xffJ\xff\xff\xff\xffK\x00t\x94b\x89C(\x13a\xf9H,\x05\x00\x00(\xe0\x1eI,\x05\x00\x00]\xe0\x1eI,\x05\x00\x00^\xe0\x1eI,\x05\x00\x00w\xe0\x1eI,\x05\x00\x00\x94t\x94bh9K\x00K\x01K\x01\x87\x94R\x94K\x02\x87\x94R\x94t\x94]\x94(\x8c\x18pandas.core.indexes.base\x94\x8c\n_new_Index\x94\x93\x94hz\x8c\x05Index\x94\x93\x94}\x94(\x8c\x04data\x94h"h$K\x00\x85\x94h&\x87\x94R\x94(K\x01K\x08\x85\x94h\x16\x8c\x02O8\x94\x89\x88\x87\x94R\x94(K\x03\x8c\x01|\x94NNNJ\xff\xff\xff\xffJ\xff\xff\xff\xffK?t\x94b\x89]\x94(\x8c\x08updateId\x94\x8c\tpublishTs\x94\x8c\nreceivedTs\x94\x8c\x10matchingEngineTs\x94\x8c\x08bidPrice\x94\x8c\x08askPrice\x94\x8c\x08midPrice\x94\x8c\x02ts\x94et\x94b\x8c\x04name\x94Nu\x86\x94R\x94h|\x8c\x19pandas.core.indexes.range\x94\x8c\nRangeIndex\x94\x93\x94}\x94(h\x94N\x8c\x05start\x94K\x00\x8c\x04stop\x94K\x05\x8c\x04step\x94K\x01u\x86\x94R\x94e\x86\x94R\x94\x8c\x04_typ\x94\x8c\tdataframe\x94\x8c\t_metadata\x94]\x94\x8c\x05attrs\x94}\x94\x8c\x06_flags\x94}\x94\x8c\x17allows_duplicate_labels\x94\x88sub.'
        org_df = pickle.loads(df_bytes)

        file_path = os.path.join(dirPath, 'parquet_with_time.parquet')
        saveobj.dump(org_df, path=file_path)
        pq_df = saveobj.load(file_path)
        assert org_df.equals(pq_df)
