import os
import tempfile

import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.transformer.info import Info
from anre.utils.modeling.transformer.iTransformer import ITransformer
from anre.utils.modeling.transformer.transformer import Transformer
from anre.utils.modeling.transformer.transformers.ecdf import Ecdf
from anre.utils.modeling.transformer.transformers.sklearnGeneral import SklearnGeneral


class TestIdentity(testutil.TestCase):
    X_np: np.ndarray
    X_pd: pd.DataFrame
    y_np: np.ndarray
    y_pd: pd.Series
    mainDirPath: str
    _rootDirPath: str

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        nRows = 60
        nCols = 5
        X_np = np.random.rand(nRows, nCols)
        X_pd = pd.DataFrame(X_np, columns=[f'x{i}' for i in range(X_np.shape[1])])
        y_np = np.random.rand(nRows)
        y_pd = pd.Series(y_np)

        rootDirPath = tempfile.mkdtemp(suffix=None, prefix=None, dir=None)
        mainDirPath = os.path.join(rootDirPath, 'someDir', 'deeperDir')

        cls.X_np = X_np
        cls.X_pd = X_pd
        cls.y_np = y_np
        cls.y_pd = y_pd
        cls.mainDirPath = mainDirPath
        cls._rootDirPath = rootDirPath

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        FileSystem.delete_folder(path=cls._rootDirPath, ignore_errors=True)
        assert not os.path.exists(cls._rootDirPath)

    def test_transformerManager(self) -> None:
        with self.assertRaises(NotImplementedError):
            Transformer.new_fromClassId(classId='None')

    def test_identity(self) -> None:
        transformer = Transformer.new_identity()
        self._test_transformer_X(transformer=transformer, exactRevers=True)
        self._test_transformer_y(transformer=transformer, exactRevers=True)

    def test_sklearnGeneral(self) -> None:
        transformer = Transformer.new_sklearnGeneral()
        self._test_transformer_X(transformer=transformer, exactRevers=True)
        self._test_transformer_y(transformer=transformer, exactRevers=True)

    def test_sklearnGeneral_scaler(self) -> None:
        transformer = SklearnGeneral.new_scaler()
        self._test_transformer_X(transformer=transformer, exactRevers=True)
        self._test_transformer_y(transformer=transformer, exactRevers=True)

    def test_sklearnGeneral_pca(self) -> None:
        transformer = SklearnGeneral.new_selectPca(nComponents=None)
        self._test_transformer_X(transformer=transformer, exactRevers=True)
        self._test_transformer_y(transformer=transformer, exactRevers=True)

        transformer = SklearnGeneral.new_selectPca(nComponents=2)
        self._test_transformer_X(transformer=transformer, exactRevers=False)
        # self._test_transformer_y(transformer=transformer, exactRevers=False)

    def test_sklearnGeneral_pca_subset(self) -> None:
        transformer = SklearnGeneral.new_selectPca(nComponents=2, pcaFields=slice(0, 3))
        self._test_transformer_X(transformer=transformer, exactRevers=False, skipReverse=True)

    def test_sklearnGeneral_scalePca(self) -> None:
        transformer = SklearnGeneral.new_scalePca()
        self._test_transformer_X(transformer=transformer, exactRevers=True)
        self._test_transformer_y(transformer=transformer, exactRevers=True)

        transformer = SklearnGeneral.new_scalePca(nComponents=2)
        self._test_transformer_X(transformer=transformer, exactRevers=False)
        # elf._test_transformer_y(transformer=transformer, exactRevers=False)

    def test_ecdf(self) -> None:
        transformer = Ecdf.new()
        self._test_transformer_y(transformer=transformer, exactRevers=False)

    def _test_transformer_X(
        self, transformer: ITransformer, exactRevers: bool = True, skipReverse: bool = False
    ):
        X_np = self.X_np
        X_pd = self.X_pd

        self._test_transformer_onData(
            transformer=transformer, X=X_np, exactRevers=exactRevers, skipReverse=skipReverse
        )
        self._test_transformer_onData(
            transformer=transformer, X=X_pd, exactRevers=exactRevers, skipReverse=skipReverse
        )

    def _test_transformer_y(
        self, transformer: ITransformer, exactRevers: bool = True, skipReverse: bool = False
    ):
        y_np = self.y_np
        y_pd = self.y_pd

        self._test_transformer_onData(
            transformer=transformer, X=y_np, exactRevers=exactRevers, skipReverse=skipReverse
        )
        self._test_transformer_onData(
            transformer=transformer, X=y_pd, exactRevers=exactRevers, skipReverse=skipReverse
        )

    def _test_transformer_onData(
        self, transformer: ITransformer, X, exactRevers=True, skipReverse=False
    ):
        mainDirPath = self.mainDirPath

        self.assertIsInstance(transformer, ITransformer)
        transformerClass = transformer.__class__
        dirPath = os.path.join(mainDirPath, transformerClass.__name__)
        self.assertTrue(not os.path.exists(dirPath))

        _transformer = transformer.recreate()
        self.assertIsInstance(_transformer, ITransformer)
        self.assertTrue(not _transformer.isFitted)

        transformer1 = transformer.copy()
        self.assertIsInstance(transformer1, ITransformer)
        self.assertTrue(transformer1 is not transformer)
        del transformer

        ### members
        self.assertIsInstance(transformer1.isFitted, bool)
        self.assertIsInstance(transformer1.classId, str)
        self.assertIsInstance(transformer1.get_info(), Info)
        self.assertTrue(transformer1.isFitted is False)

        ### fit and transform
        with self.assertRaises(AssertionError):
            transformer1.transform(X)
        with self.assertRaises(AssertionError):
            transformer1.inverse_transform(X)
        with self.assertRaises(AssertionError):
            transformer1.save(dirPath=dirPath)

        obj = transformer1.fit(X)
        self.assertTrue(obj is transformer1)
        self.assertTrue(transformer1.isFitted is True)
        with self.assertRaises(AssertionError):
            transformer1.fit(X)

        # transform
        xTrans1 = transformer1.transform(X)
        self.assertIsInstance(xTrans1, (pd.DataFrame, pd.Series, np.ndarray))
        self.assertTrue(xTrans1.shape[0] == X.shape[0])

        # reverse
        if not skipReverse:
            altX1 = transformer1.inverse_transform(xTrans1)
            self.assertIsInstance(altX1, (pd.DataFrame, pd.Series, np.ndarray))
            self.assertTrue(altX1.shape == X.shape)
            if exactRevers:
                self.assertTrue(np.all(np.max(np.abs(altX1 - X), axis=0) < 1e-5))

        ### save and load
        self.assertTrue(not os.path.exists(dirPath))
        transformer1.save(dirPath=dirPath)
        self.assertTrue(os.path.exists(dirPath))

        # re-save
        with self.assertRaises(FileExistsError):
            transformer1.save(dirPath=dirPath)
        transformer1.save(dirPath=dirPath, overwrite=True)

        transformer2 = transformerClass.load(dirPath)
        self.assertIsInstance(transformer2, transformerClass)
        self.assertTrue(transformer2.isFitted is True)
        xTrans2 = transformer2.transform(X)
        self.assertIsInstance(xTrans2, (pd.DataFrame, pd.Series, np.ndarray))
        self.assertTrue(np.all(np.max(np.abs(xTrans2 - xTrans1), axis=0) < 1e-5))
        if not skipReverse:
            altX2 = transformer1.inverse_transform(xTrans2)
            self.assertIsInstance(altX2, (pd.DataFrame, pd.Series, np.ndarray))
            self.assertTrue(np.all(np.max(np.abs(altX2 - altX1), axis=0) < 1e-5))

        transformer3 = Transformer.load(dirPath)
        self.assertIsInstance(transformer3, transformerClass)
        self.assertTrue(transformer3.isFitted is True)
        xTrans3 = transformer3.transform(X)
        self.assertIsInstance(xTrans3, (pd.DataFrame, pd.Series, np.ndarray))
        self.assertTrue(np.all(np.max(np.abs(xTrans3 - xTrans1), axis=0) < 1e-5))
        if not skipReverse:
            altX3 = transformer1.inverse_transform(xTrans3)
            self.assertIsInstance(altX3, (pd.DataFrame, pd.Series, np.ndarray))
            self.assertTrue(np.all(np.max(np.abs(altX3 - altX1), axis=0) < 1e-5))

        transformer4 = transformer1.copy()
        self.assertIsInstance(transformer4, transformerClass)
        self.assertTrue(transformer4.isFitted is True)
        xTrans4 = transformer4.transform(X)
        self.assertIsInstance(xTrans4, (pd.DataFrame, pd.Series, np.ndarray))
        self.assertTrue(np.all(np.max(np.abs(xTrans4 - xTrans1), axis=0) < 1e-5))
        if not skipReverse:
            altX4 = transformer1.inverse_transform(xTrans4)
            self.assertIsInstance(altX4, (pd.DataFrame, pd.Series, np.ndarray))
            self.assertTrue(np.all(np.max(np.abs(altX4 - altX1), axis=0) < 1e-5))

        # recreate fitted
        transformer5 = transformer1.recreate()
        self.assertIsInstance(transformer5, transformerClass)
        self.assertTrue(transformer5.isFitted is False)
        with self.assertRaises(AssertionError):
            transformer5.transform(X)

        # recreate loaded
        transformer5 = transformer4.recreate()
        self.assertIsInstance(transformer5, transformerClass)
        self.assertTrue(transformer5.isFitted is False)
        with self.assertRaises(AssertionError):
            transformer5.transform(X)

        transformer6 = Transformer.new_fromClassId(classId=transformerClass.classId)
        self.assertIsInstance(transformer6, transformerClass)
        self.assertTrue(transformer6.isFitted is False)

        FileSystem.delete_folder(path=dirPath, ignore_errors=False)
