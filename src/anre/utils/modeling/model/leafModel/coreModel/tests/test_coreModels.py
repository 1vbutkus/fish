# mypy: disable-error-code="assignment"
import os
import tempfile

import numpy as np
import pandas as pd
import pytest

from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.leafModel.coreModel.coreModel import CoreModel
from anre.utils.modeling.model.leafModel.coreModel.coreModels.lgbmClassificationBinary import (
    LgbmClassificationBinary,
)
from anre.utils.modeling.model.leafModel.coreModel.coreModels.lgbmRegression import LgbmRegression
from anre.utils.modeling.model.leafModel.coreModel.coreModels.sklearnGeneral import SklearnGeneral
from anre.utils.modeling.model.leafModel.coreModel.iCoreModel import ICoreModel
from anre.utils.modeling.model.leafModel.coreModel.info import Info


class TestCoreModel(testutil.TestCase):
    X: np.ndarray
    y: np.ndarray
    xDf: pd.DataFrame
    ySr: pd.Series
    mainDirPath: str
    _rootDirPath: str

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        nRows = 60
        nCols = 5
        X = np.random.rand(nRows, nCols)
        y = (np.random.rand(nRows) > 0.5) * 1
        xDf = pd.DataFrame(X)
        xDf.columns = [f'[{el}]' for el in xDf.columns]
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

    def test_coreModel_master(self) -> None:
        with self.assertRaises(NotImplementedError):
            CoreModel.new_fromEngine(engine=None)

    def test_SklearnGeneral(self) -> None:
        xDf = self.xDf
        ySr = self.ySr

        _ = self._test_common_model(coreModel=SklearnGeneral.new_pipe())
        _ = self._test_common_model(coreModel=SklearnGeneral.new_model())
        model = self._test_common_model(coreModel=SklearnGeneral.new())

        engine = model.get_engine()
        model5 = CoreModel.new_fromEngine(engine=engine)
        self.assertIsInstance(model5, model.__class__)
        self.assertTrue(not model5.isFitted)

        with self.assertRaises(NotImplementedError):
            model.get_featureImportanceSr()

        with self.assertRaises(NotImplementedError):
            model.fit_continue(xDf, ySr)

        # recreated copy
        _model = model.copy().recreate()
        self.assertIsInstance(_model, model.__class__)
        self.assertTrue(not _model.isFitted)

    @pytest.mark.slow
    def test_LgbmRegression(self) -> None:
        xDf = self.xDf
        ySr = self.ySr

        model = self._test_common_model(coreModel=LgbmRegression.new())
        model.get_featureImportanceSr()

        engine = model.get_engine()
        model5 = CoreModel.new_fromEngine(engine=engine)
        self.assertIsInstance(model5, model.__class__)
        self.assertTrue(not model5.isFitted)

        with self.assertRaises(NotImplementedError):
            model.fit_continue(xDf, ySr)

        # recreated copy
        _model = model.copy().recreate()
        self.assertIsInstance(_model, model.__class__)
        self.assertTrue(not _model.isFitted)

    @pytest.mark.slow
    def test_LgbmClassificationBinary(self) -> None:
        xDf = self.xDf
        ySr = self.ySr

        model = self._test_common_model(coreModel=LgbmClassificationBinary.new())
        model.get_featureImportanceSr()

        engine = model.get_engine()
        model5 = CoreModel.new_fromEngine(engine=engine)
        self.assertIsInstance(model5, model.__class__)
        self.assertTrue(not model5.isFitted)

        with self.assertRaises(NotImplementedError):
            model.fit_continue(xDf, ySr)

        # recreated copy
        _model = model.copy().recreate()
        self.assertIsInstance(_model, model.__class__)
        self.assertTrue(not _model.isFitted)

    def _test_common_model(self, coreModel: ICoreModel):
        X = self.X
        y = self.y
        xDf = self.xDf
        ySr = self.ySr

        _ = self._test_modelWithData(coreModel=coreModel, X=X, y=y)
        resModel = self._test_modelWithData(coreModel=coreModel, X=xDf, y=ySr)

        return resModel

    def _test_modelWithData(self, coreModel: ICoreModel, X, y):
        mainDirPath = self.mainDirPath
        modelClass = coreModel.__class__
        dirPath = os.path.join(mainDirPath, modelClass.__name__)
        assert not os.path.exists(dirPath)

        assert isinstance(coreModel, ICoreModel)

        # recreate fresh strategy
        _model = coreModel.recreate()
        self.assertIsInstance(_model, modelClass)
        self.assertTrue(not _model.isFitted)

        # make clean copy
        model0 = coreModel.copy()
        self.assertTrue(model0 is not coreModel)
        self.assertIsInstance(_model, modelClass)
        self.assertTrue(not _model.isFitted)

        # proc
        model1 = model0.copy()
        self.assertTrue(model1 is not model0)
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
        assert modelClass.isValidEngine(engine=engine)

        pred1 = model1.predict(X)
        self.assertTrue(pred1.shape == (X.shape[0],))

        # save with variations
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

        model3 = CoreModel.load(dirPath)
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

        # recreate fitted
        model6 = model1.recreate()
        self.assertIsInstance(model6, modelClass)
        self.assertTrue(not model6.isFitted)

        model6 = CoreModel.new_fromModelClassId(classId=model1.classId)
        self.assertIsInstance(model6, modelClass)
        self.assertTrue(not model6.isFitted)

        FileSystem.delete_folder(path=dirPath, ignore_errors=False)

        return model1
