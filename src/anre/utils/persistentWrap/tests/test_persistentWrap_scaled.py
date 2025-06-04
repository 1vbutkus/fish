import os
import tempfile

import pandas as pd

from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.persistentWrap.persistentWrap import PersistentWrap
from anre.utils.worker.worker import Worker


class TestPersistentWrap(testutil.TestCase):
    rootDitPath: str

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        rootDitPath = tempfile.mkdtemp()
        cls.rootDitPath = rootDitPath

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        FileSystem.delete_folder(path=cls.rootDitPath, ignore_errors=True)
        assert not os.path.exists(cls.rootDitPath)

    def test_get_fun_res_list_on_cashed(self) -> None:
        rootDitPath = self.rootDitPath

        worker = Worker.new_sequential(show_progress=False)
        cacheDirPath = os.path.join(rootDitPath, 'PersistentWrap_1')
        counterDict = {'count': 0}

        @PersistentWrap.decorator(cache_dir_path=cacheDirPath)
        def fun(a, b, c):
            counterDict['count'] += 1
            return a + b + c

        resList = PersistentWrap.get_fun_res_list(
            fun=fun,
            kwargs_list=[{'c': 1}, {'c': 2}, {'c': 3}],
            reset_cache=False,
            worker=worker,
            a=0,
            b=0,
        )
        self.assertEqual(counterDict['count'], 3)
        self.assertEqual(len(resList), 3)

        res_act = PersistentWrap.get_fun_res_exist_list(
            fun=fun,
            kwargs_list=[{'c': 1}, {'c': 2}, {'c': 3}, {'c': 4}],
            a=0,
            b=0,
        )
        assert res_act == [True, True, True, False]

    def test_basicFunctions(self) -> None:
        rootDitPath = self.rootDitPath

        worker = Worker.new_sequential(show_progress=False)

        counterDict = {'count': 0}

        def fun(a, b, c):
            counterDict['count'] += 1
            return a + b + c

        cacheDirPath = os.path.join(rootDitPath, 'PersistentWrap_1')

        resList = PersistentWrap.get_fun_res_list(
            fun=fun,
            kwargs_list=[{'c': 1}, {'c': 2}, {'c': 3}],
            cache_dir_path=cacheDirPath,
            reset_cache=False,
            worker=worker,
            a=0,
            b=0,
            verbose=True,
        )
        self.assertEqual(counterDict['count'], 3)
        self.assertEqual(len(resList), 3)

        res_act = PersistentWrap.get_fun_res_exist_list(
            fun=fun,
            kwargs_list=[{'c': 1}, {'c': 2}, {'c': 3}, {'c': 4}],
            cache_dir_path=cacheDirPath,
            a=0,
            b=0,
        )
        assert res_act == [True, True, True, False]

        resDict = PersistentWrap.get_fun_res_list(
            fun=fun,
            kwargs_list=[{'c': 1}, {'c': 2}, {'c': 3}],
            cache_dir_path=cacheDirPath,
            reset_cache=False,
            worker=worker,
            a=0,
            b=0,
        )
        self.assertEqual(counterDict['count'], 3)
        self.assertEqual(len(resDict), 3)

        resList = PersistentWrap.get_fun_res_list(
            fun=fun,
            kwargs_list=[{'c': 1}, {'c': 2}, {'c': 4}],
            cache_dir_path=cacheDirPath,
            reset_cache=False,
            worker=worker,
            a=0,
            b=0,
        )
        self.assertEqual(counterDict['count'], 4)
        self.assertEqual(len(resList), 3)

        resList = PersistentWrap.get_fun_res_list(
            fun=fun,
            kwargs_list=[{'c': 1}, {'c': 2}, {'c': 4}],
            cache_dir_path=cacheDirPath,
            reset_cache=False,
            worker=worker,
            a=1,
            b=1,
        )
        self.assertEqual(counterDict['count'], 7)
        self.assertEqual(len(resList), 3)

    def test_withErrors(self) -> None:
        rootDitPath = self.rootDitPath
        cacheDirPath = os.path.join(rootDitPath, 'PersistentWrap_2')

        worker = Worker.new_sequential(show_progress=False)

        counterDict = {'count': 0}

        def fun(a, b, c):
            counterDict['count'] += 1
            return a + b + c

        with self.assertWarns(Warning):
            resList = PersistentWrap.get_fun_res_list(
                fun=fun,
                kwargs_list=[{'c': 1}, {'c': 2}, {'c': 'a'}],
                cache_dir_path=cacheDirPath,
                reset_cache=False,
                worker=worker,
                a=0,
                b=0,
            )
        self.assertEqual(counterDict['count'], 3)
        self.assertEqual(len(resList), 3)

        # we repeat the same call and look how much function runs was used
        resList = PersistentWrap.get_fun_res_list(
            fun=fun,
            kwargs_list=[{'c': 1}, {'c': 2}, {'c': 'a'}, {'c': 1}],
            cache_dir_path=cacheDirPath,
            reset_cache=False,
            worker=worker,
            rerun_if_failed=False,
            a=0,
            b=0,
        )
        self.assertEqual(counterDict['count'], 3)
        self.assertEqual(len(resList), 4)

        # we repeat the same call and look how much function runs was used
        with self.assertWarns(Warning):
            resList = PersistentWrap.get_fun_res_list(
                fun=fun,
                kwargs_list=[{'c': 1}, {'c': 2}, {'c': 'a'}],
                cache_dir_path=cacheDirPath,
                reset_cache=False,
                worker=worker,
                rerun_if_failed=True,
                a=0,
                b=0,
            )
        self.assertEqual(counterDict['count'], 4)
        self.assertEqual(len(resList), 3)

    def test_pandas(self) -> None:
        rootDitPath = self.rootDitPath
        cacheDirPath = os.path.join(rootDitPath, 'PersistentWrap_3')

        worker = Worker.new_sequential(show_progress=False)

        def fun_pandas(a):
            return pd.Series(range(3))

        _ = PersistentWrap.get_fun_res_list(
            fun=fun_pandas,
            kwargs_list=[{'a': 1}, {'a': 2}, {'a': 3}],
            cache_dir_path=cacheDirPath,
            reset_cache=False,
            worker=worker,
        )

        _ = PersistentWrap.get_fun_res_list(
            fun=fun_pandas,
            kwargs_list=[{'a': 1}, {'a': 2}, {'a': 3}],
            cache_dir_path=cacheDirPath,
            reset_cache=False,
            worker=worker,
        )
