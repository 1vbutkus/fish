import inspect
import os
import tempfile
from typing import Any

from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.persistentWrap.persistentWrap import PersistentWrap


class TestPersistentWrapDecorator(testutil.TestCase):
    cacheDir: str

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cacheDir = tempfile.mkdtemp()
        cls.cacheDir = cacheDir

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        FileSystem.delete_folder(path=cls.cacheDir, ignore_errors=True)
        assert not os.path.exists(cls.cacheDir)

    def test_manual_decor(self) -> None:
        cacheDir = self.cacheDir

        dataDict = dict(counter=0)

        def manual_decor_fun(x) -> Any:
            """Document"""
            dataDict['counter'] += 1
            return x

        wrapper = PersistentWrap.decorator(cache_dir_path=cacheDir)(manual_decor_fun)
        assert wrapper.__doc__ == "Document"
        assert inspect.signature(wrapper).return_annotation is Any

        assert dataDict['counter'] == 0
        wrapper(1)
        assert dataDict['counter'] == 1
        wrapper(1)
        assert dataDict['counter'] == 1
        wrapper(2)
        assert dataDict['counter'] == 2

    def test_mutable_arg(self) -> None:
        cacheDir = self.cacheDir

        dataDict = dict(counter=0)

        def count(x: list):
            dataDict['counter'] += 1
            return len(x)

        wrapper = PersistentWrap.decorator(cache_dir_path=cacheDir)(count)
        x = [1, 2, 3]

        assert dataDict['counter'] == 0
        ans = wrapper(x)
        assert ans == 3
        assert dataDict['counter'] == 1

        x.append(4)
        ans = wrapper(x)
        assert ans == 4
        assert dataDict['counter'] == 2

        ans = wrapper([1, 2, 3])
        assert ans == 3
        assert dataDict['counter'] == 2

    def test_decorator_basic(self) -> None:
        cacheDir = self.cacheDir
        dataDict = dict(counter=0)

        @PersistentWrap.decorator(cache_dir_path=cacheDir)
        def someFunction(x):
            """Document"""
            dataDict['counter'] += 1
            return x

        assert someFunction.__doc__ == "Document"

        self.assertEqual(0, dataDict['counter'])

        _ = someFunction(x=0, _use_cache=1)
        self.assertEqual(1, dataDict['counter'])

        _ = someFunction(x=0, _use_cache=1)
        self.assertEqual(1, dataDict['counter'])

        _ = someFunction(x=1, _use_cache=1)
        self.assertEqual(2, dataDict['counter'])

        _ = someFunction(x=1, _use_cache=1)
        self.assertEqual(2, dataDict['counter'])

        _ = someFunction(x=1, _use_cache=0)
        self.assertEqual(3, dataDict['counter'])

        _ = someFunction(x=1, _use_cache=0)
        self.assertEqual(4, dataDict['counter'])

        _ = someFunction(x=1, _use_cache=1, _check_prob=1, _verbose=True)
        self.assertEqual(5, dataDict['counter'])

    def test_decorator_class(self) -> None:
        cacheDir = self.cacheDir
        dataDict = dict(counter=0)

        class A:
            @staticmethod
            @PersistentWrap.decorator(cache_dir_path=cacheDir)
            def staticFun(xyz, *args: Any, y=1, **kwargs: Any):
                dataDict['counter'] += 1
                return xyz + y

            @classmethod
            @PersistentWrap.decorator(cache_dir_path=cacheDir)
            def clsFun(cls, xyz, *args: Any, y=1, **kwargs: Any):
                dataDict['counter'] += 1
                return xyz + y

            @PersistentWrap.decorator(cache_dir_path=cacheDir)
            def selfFun(self, xyz, *args: Any, y=1, **kwargs: Any):
                dataDict['counter'] += 1
                return xyz + y

        self.assertEqual(0, dataDict['counter'])

        res = A.staticFun(1, _use_cache=1)
        assert res == 2
        self.assertEqual(1, dataDict['counter'])

        res = A.staticFun(xyz=1, _use_cache=1)
        assert res == 2
        self.assertEqual(1, dataDict['counter'])

        res = A.staticFun(y=1, xyz=1, _use_cache=1)
        assert res == 2
        self.assertEqual(1, dataDict['counter'])

        ### class

        res = A.clsFun(y=1, xyz=1, _use_cache=1)
        assert res == 2
        self.assertEqual(2, dataDict['counter'])

        a = A()
        res = a.clsFun(y=1, xyz=1, _use_cache=1)
        assert res == 2
        self.assertEqual(2, dataDict['counter'])

        ### instance
        a = A()
        with self.assertRaises(AssertionError):
            res = a.selfFun(y=1, xyz=1, _use_cache=1)

    def test_decorator_default(self) -> None:
        cacheDir = self.cacheDir
        dataDict = dict(counter=0)

        @PersistentWrap.decorator(cache_dir_path=cacheDir, default_use_cache=1)
        def someFunctionWithCacheByDefault(x):
            dataDict['counter'] += 1
            return x

        self.assertEqual(0, dataDict['counter'])

        _ = someFunctionWithCacheByDefault(1)
        self.assertEqual(1, dataDict['counter'])

        _ = someFunctionWithCacheByDefault(1)
        self.assertEqual(1, dataDict['counter'])

    def test_decorator_noArgument(self) -> None:
        cacheDir = self.cacheDir
        dataDict = dict(counter=0)

        @PersistentWrap.decorator(cache_dir_path=cacheDir, default_use_cache=1)
        def someFunctionNoArgument():
            """Document"""
            dataDict['counter'] += 1
            return 1

        self.assertEqual(0, dataDict['counter'])

        _ = someFunctionNoArgument()
        self.assertEqual(1, dataDict['counter'])

        _ = someFunctionNoArgument()
        self.assertEqual(1, dataDict['counter'])

    def test_decorator_skip_args(self) -> None:
        cacheDir = self.cacheDir
        dataDict = dict(counter=0)

        @PersistentWrap.decorator(cache_dir_path=cacheDir, default_use_cache=1, skip_args=['b'])
        def someFunctionNoArgument(a, b):
            """Document"""
            dataDict['counter'] += 1
            return 1

        self.assertEqual(0, dataDict['counter'])

        _ = someFunctionNoArgument(a=1, b=1)
        self.assertEqual(1, dataDict['counter'])

        _ = someFunctionNoArgument(a=1, b=2)
        self.assertEqual(1, dataDict['counter'])

    def test_decorator_kwargs(self) -> None:
        cacheDir = self.cacheDir
        dataDict = dict(counter=0)

        @PersistentWrap.decorator(cache_dir_path=cacheDir, default_use_cache=1)
        def someFunctionWithKwargs(*arg, **kw):
            """Document"""
            dataDict['counter'] += 1
            return set(kw)

        self.assertEqual(0, dataDict['counter'])

        assert set() == someFunctionWithKwargs()
        self.assertEqual(1, dataDict['counter'])

        assert set('a') == someFunctionWithKwargs(a=2)
        self.assertEqual(2, dataDict['counter'])

        assert set('ab') == someFunctionWithKwargs(a=1, b=2)
        self.assertEqual(3, dataDict['counter'])
