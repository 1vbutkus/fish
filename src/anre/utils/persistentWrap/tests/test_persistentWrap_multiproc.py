import os
import pickle
import tempfile

from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.persistentWrap.persistentWrap import PersistentWrap
from anre.utils.worker.worker import Worker

globalCounterDict = {'count': 0}


def globalSumFun(a, b, c):
    return a + b + c


@PersistentWrap.decorator()
def cashedGlobalSumFun(a, b, c):
    return a + b + c


def envelop_cashedGlobalSumFun(a, b, c):
    return cashedGlobalSumFun(a, b, c)


def globalSumFun_withCounter(a, b, c):
    globalCounterDict['count'] += 1
    return a + b + c


class TestPersistentWrap(testutil.TestCase):
    root_dir_path: str

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        root_dir_path = tempfile.mkdtemp()
        cls.root_dir_path = root_dir_path

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        FileSystem.delete_folder(path=cls.root_dir_path, ignore_errors=True)
        assert not os.path.exists(cls.root_dir_path)

    def test_pickle_simple_fun(self) -> None:
        dump = pickle.dumps(globalSumFun)
        _ = pickle.loads(dump)

    # def test_pickle_cashed_fun(self) -> None:
    #     dump = pickle.dumps(cashedGlobalSumFun)
    #     _ = pickle.loads(dump)

    def test_pickle_envelop_cashed_fun(self) -> None:
        dump = pickle.dumps(envelop_cashedGlobalSumFun)
        _ = pickle.loads(dump)

    # def test_multiproc_cashed(self) -> None:
    #     worker = Worker.new_multiproc(show_progress=False)
    #     res_act = worker.starmap(cashedGlobalSumFun, [(1, 2, 3), (4, 5, 6)])
    #     res_exp = [6, 15]
    #     assert res_act == res_exp

    def test_multiproc_envelop(self) -> None:
        worker = Worker.new_multiproc(show_progress=False)
        res_act = worker.starmap(envelop_cashedGlobalSumFun, [(1, 2, 3), (4, 5, 6)])
        res_exp = [6, 15]
        assert res_act == res_exp

    def test_multiproc_scale_simple(self) -> None:
        root_dir_path = self.root_dir_path

        worker = Worker.new_multiproc(show_progress=False)
        cacheDirPath = os.path.join(root_dir_path, 'PersistentWrap_1')

        resList = PersistentWrap.get_fun_res_list(
            fun=globalSumFun,
            kwargs_list=[{'c': 1}, {'c': 2}, {'c': 3}],
            cache_dir_path=cacheDirPath,
            reset_cache=False,
            worker=worker,
            a=0,
            b=0,
        )
        self.assertEqual(len(resList), 3)

    def test_multiproc_scale_cached(self) -> None:
        worker = Worker.new_multiproc(show_progress=False)

        resList = PersistentWrap.get_fun_res_list(
            fun=cashedGlobalSumFun,
            kwargs_list=[{'c': 1}, {'c': 2}, {'c': 3}],
            cache_dir_path=None,
            reset_cache=False,
            worker=worker,
            a=0,
            b=0,
        )
        self.assertEqual(len(resList), 3)

    def test_multiproc_scale_envelop(self) -> None:
        root_dir_path = self.root_dir_path

        worker = Worker.new_multiproc(show_progress=False)
        cacheDirPath = os.path.join(root_dir_path, 'PersistentWrap_1')

        resList = PersistentWrap.get_fun_res_list(
            fun=envelop_cashedGlobalSumFun,
            kwargs_list=[{'c': 1}, {'c': 2}, {'c': 3}],
            cache_dir_path=cacheDirPath,
            reset_cache=False,
            worker=worker,
            a=0,
            b=0,
        )
        self.assertEqual(len(resList), 3)
