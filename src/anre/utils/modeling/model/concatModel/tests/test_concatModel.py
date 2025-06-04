import os
import tempfile
from typing import Any

import numpy as np
import pandas as pd
import pytest

from anre.utils import pandas_ as pdu
from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.concatModel.concatModel import ConcatModel
from anre.utils.modeling.model.leafModel.leafModel import LeafModel


@pytest.mark.slow
class TestConcatModel(testutil.TestCase):
    rootDirPath: str
    dirPath: str

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        rootDirPath = tempfile.mkdtemp()
        dirPath = os.path.join(rootDirPath, 'someDir', 'deeperDir')

        cls.rootDirPath = rootDirPath
        cls.dirPath = dirPath

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        FileSystem.delete_folder(path=cls.rootDirPath, ignore_errors=True)
        assert not os.path.exists(cls.rootDirPath)

    def test_new_buildFit_fromLeafModel(self) -> None:
        dataDf = pdu.new.get_randomDf(shape=(25, 5))
        dataDf.rename(columns={'x3': 'y0', 'x4': 'y1'}, inplace=True)
        xFields = ['x0', 'x1', 'x2']
        yields = ['y0', 'y1']
        buildKwargs: dict[str, Any] = {
            'min_child_samples': 2,
            'n_estimators': 10,
        }
        # add na
        dataDf.loc[3, 'y1'] = np.nan

        concatModel = ConcatModel.new_buildFit_fromLeafModel(
            model=LeafModel.new_lgbmRegression(**buildKwargs),
            X=dataDf[xFields],
            Y=dataDf[yields],
            fitKwargs=None,
            dropTargetNa=True,
        )
        self._testModel_reload(concatModel=concatModel, dataDf=dataDf)

        predAr = concatModel.predict(dataDf)
        assert isinstance(predAr, np.ndarray)
        assert predAr.shape == (dataDf.shape[0], 2)

        predictDf = concatModel.get_predictDf(dataDf)
        assert isinstance(predictDf, pd.DataFrame)
        assert predictDf.shape == predAr.shape
        assert np.max(np.abs(predictDf.values - predAr)) < 1e-7

    def test_customConstruct(self) -> None:
        dataDf = pdu.new.get_randomDf(shape=(25, 5))
        dataDf.rename(columns={'x3': 'y0', 'x4': 'y1'}, inplace=True)
        xFields = ['x0', 'x1', 'x2']
        hp: dict[str, Any] = {
            'min_child_samples': 2,
            'n_estimators': 10,
        }

        model0 = LeafModel.new_lgbmRegression(**hp)
        model0.fit(dataDf[xFields], dataDf['y0'])

        model1 = LeafModel.new_lgbmRegression(**hp)
        model1.fit(dataDf[xFields], dataDf['y1'])

        models = [model0, model1]
        concatModel1 = ConcatModel.new_fromList(models=models)
        self._testModel_reload(concatModel=concatModel1, dataDf=dataDf)

        models = [concatModel1, model0, model1]
        concatModel2 = ConcatModel.new_fromList(models=models)
        self._testModel_reload(concatModel=concatModel2, dataDf=dataDf)

        predAr = concatModel2.predict(dataDf)
        assert isinstance(predAr, np.ndarray)
        assert predAr.shape == (dataDf.shape[0], 4)
        assert np.all(predAr[:, 0] == predAr[:, 2])
        _predOrg0 = model0.predict(dataDf)
        assert np.all(predAr[:, 0] == _predOrg0)

    def _testModel_reload(self, concatModel: ConcatModel, dataDf: pd.DataFrame):
        dirPath = self.dirPath

        _dirPath = os.path.join(dirPath, 'mmooddeell')
        concatModel.save(dirPath=_dirPath)

        concatModel_alt = ConcatModel.load(dirPath=_dirPath)
        assert isinstance(concatModel_alt, ConcatModel)

        pred1 = concatModel.predict(dataDf)
        pred2 = concatModel_alt.predict(dataDf)
        assert np.all(pred2 == pred1)

        FileSystem.delete_folder(_dirPath)
