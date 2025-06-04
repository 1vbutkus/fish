import os
import tempfile

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.leafModel.info import Info
from anre.utils.modeling.model.leafModel.leafModel import LeafModel


class TestModel(testutil.TestCase):
    _rootDirPath: str
    mainDirPath: str
    X: np.ndarray
    y: np.ndarray
    xDf: pd.DataFrame
    ySr: pd.Series

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        nRows = 60
        nCols = 7
        X = np.random.rand(nRows, nCols)
        y = (np.random.rand(nRows) > 0.5) * 1
        xDf = pd.DataFrame(X, columns=[f'x{i}' for i in range(nCols)])
        ySr = pd.Series(y)

        rootDirPath = tempfile.mkdtemp(suffix=None, prefix=None, dir=None)
        mainDirPath = os.path.join(rootDirPath, 'someDir', 'deeperDir')

        cls.X = X
        cls.y = y
        cls.xDf = xDf
        cls.ySr = ySr
        cls.mainDirPath = mainDirPath
        cls._rootDirPath = rootDirPath

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        FileSystem.delete_folder(path=cls._rootDirPath, ignore_errors=True)
        assert not os.path.exists(cls._rootDirPath)

    @pytest.mark.slow
    def test_lgbmRegression(self) -> None:
        _model = LeafModel.new_lgbmRegression()
        model = self._test_common_model(model=_model)

        engine = model.get_engine()
        model5 = LeafModel.new_fromEngine(engine=engine)
        self.assertIsInstance(model5, model.__class__)
        self.assertTrue(not model5.isFitted)

    # def test_lgbmRegression_withTransformer(self) -> None:
    #     _model = LeafModel.new_lgbmRegression(
    #         inputTransformer=SklearnGeneralTransformer.new_selectPca(nComponents=2)
    #     )
    #     strategy = self._test_common_model(strategy=_model)
    #
    #     engine = strategy.get_engine()
    #     model5 = LeafModel.new_fromEngine(engine=engine)
    #     self.assertIsInstance(model5, strategy.__class__)
    #     self.assertTrue(not model5.isFitted)

    @pytest.mark.slow
    def test_lgbmClassificationBinary(self) -> None:
        model = self._test_common_model(model=LeafModel.new_lgbmClassificationBinary())

        engine = model.get_engine()
        model5 = LeafModel.new_fromEngine(engine=engine)
        self.assertIsInstance(model5, model.__class__)
        self.assertTrue(not model5.isFitted)

    def test_sklearnGeneral(self) -> None:
        model = self._test_common_model(model=LeafModel.new_sklearnGeneral())

        engine = model.get_engine()
        model5 = LeafModel.new_fromEngine(engine=engine)
        self.assertIsInstance(model5, model.__class__)
        self.assertTrue(not model5.isFitted)

    def test_sklearnGeneral_engine(self) -> None:
        engine = Pipeline([('scaler', RobustScaler()), ('regression', LinearRegression())])
        model = self._test_common_model(model=LeafModel.new_sklearnGeneral(engine=engine))

        engine = model.get_engine()
        model5 = LeafModel.new_fromEngine(engine=engine)
        self.assertIsInstance(model5, model.__class__)
        self.assertTrue(not model5.isFitted)

    def _test_common_model(self, model: LeafModel):
        X = self.X
        y = self.y
        xDf = self.xDf
        ySr = self.ySr

        _ = self._test_modelWithData(model=model, X=X, y=y)
        resModel = self._test_modelWithData(model=model, X=xDf, y=ySr)

        return resModel

    def _test_modelWithData(self, model: LeafModel, X, y):
        mainDirPath = self.mainDirPath
        modelClass = model.__class__
        coreModelClass = model.coreModel.__class__

        assert isinstance(model, modelClass)
        assert isinstance(model.coreModel, coreModelClass)

        _model = model.recreate()
        self.assertIsInstance(_model, modelClass)
        self.assertTrue(not _model.isFitted)

        model1 = model.copy()

        self.assertTrue(not model1.isFitted)
        with self.assertRaises(AssertionError):
            _ = model1.input_shape
        with self.assertRaises(AssertionError):
            _ = model1.output_shape

        model1.fit(X=X, y=y)
        self.assertTrue(model1.isFitted)
        self.assertTrue(len(model1.output_shape) == 1)
        self.assertTrue(len(model1.input_shape) == 2)
        self.assertTrue(X.shape[1:] == model1.input_shape[1:])

        ## members
        info = model1.get_info()
        self.assertIsInstance(info, Info)

        engine = model1.get_engine()
        with self.assertRaises(NotImplementedError):
            modelClass.isValidEngine(engine=engine)

        pred1 = model1.predict(X)
        self.assertTrue(pred1.shape == (X.shape[0],))

        ### test mixing input
        if isinstance(X, pd.DataFrame):
            X_revCol = X[list(reversed(X.columns))]
            pred1_revCol = model1.predict(X_revCol)
            self.assertTrue(np.all(pred1 == pred1_revCol))

        # save with variations
        dirPath = os.path.join(mainDirPath, coreModelClass.__name__)
        assert not os.path.exists(dirPath)
        model1.save(dirPath, overwrite=False)
        with self.assertRaises(FileExistsError):
            model1.save(dirPath, overwrite=False)
        model1.save(dirPath, overwrite=True)

        ### load and test if match
        model2 = modelClass.load(dirPath)
        self.assertIsInstance(model2, modelClass)
        assert model2.isFitted
        assert model2.input_shape == model1.input_shape
        pred2 = model2.predict(X)
        self.assertTrue(np.all(pred1 == pred2))

        model3 = LeafModel.load(dirPath)
        self.assertIsInstance(model3, modelClass)
        assert model3.input_shape == model1.input_shape
        assert model3.isFitted
        pred3 = model3.predict(X)
        self.assertTrue(np.all(pred1 == pred3))

        model4 = model3.copy()
        self.assertIsInstance(model4, modelClass)
        assert model4.input_shape == model1.input_shape
        assert model4.isFitted
        pred4 = model3.predict(X)
        self.assertTrue(np.all(pred1 == pred4))

        # fitted recreate
        model6 = model1.recreate()
        self.assertIsInstance(model6, modelClass)
        self.assertTrue(not model6.isFitted)

        model7 = LeafModel.new_fromClassId(classId=model1.coreModel.classId)
        self.assertIsInstance(model7, modelClass)
        self.assertTrue(not model7.isFitted)

        FileSystem.delete_folder(path=dirPath, ignore_errors=False)

        return model1
