import os
import tempfile
from typing import Any

import pandas as pd
import pytest

from anre.utils import pandas_ as pdu
from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.leafModel.leafModel import LeafModel
from anre.utils.modeling.model.modelHub.modelHub import ModelHub


@pytest.mark.slow
class TestModelHub(testutil.TestCase):
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

    def test_baseline(self) -> None:
        ### create sub-models
        dataDf = pdu.new.get_randomDf(shape=(25, 7))
        dataDf.rename(columns={'x5': 'y0', 'x6': 'y1'}, inplace=True)
        hp: dict[str, Any] = {
            'min_child_samples': 2,
            'n_estimators': 10,
        }
        model0 = LeafModel.new_lgbmRegression(**hp)
        model0.fit(dataDf[['x0', 'x1', 'x2']], dataDf['y0'])
        model1 = LeafModel.new_lgbmRegression(**hp)
        model1.fit(dataDf[['x3', 'x1', 'x2']], dataDf['y1'])

        # create ModelHub
        modelDict = dict(model0=model0, model1=model1)
        modelHub0 = ModelHub.new(modelDict=modelDict)
        assert isinstance(modelHub0, ModelHub)

        ### basic functions
        subModelLabels = modelHub0.subModelKeys
        assert set(subModelLabels) == {'model0', 'model1'}

        subModel = modelHub0.get_subModel(key='model0')
        assert isinstance(subModel, LeafModel)

        modelHub0.set_name(name='SuperModelHub')
        assert modelHub0.name == 'SuperModelHub'

        modelHub0.set_attrs(dict(a=1))
        assert modelHub0.attrs == dict(a=1)

        modelHub0.set_inAttrs(b=2)
        assert modelHub0.attrs == dict(a=1, b=2)

        xFieldsSet = set(modelHub0.get_xFields())
        assert xFieldsSet == {'x3', 'x2', 'x0', 'x1'}

        self._testModel_reload(modelHub=modelHub0, dataDf=dataDf)

        ### from list
        models = [model0, model1]
        modelHub1 = ModelHub.new_fromList(models=models)
        assert isinstance(modelHub1, ModelHub)

        with self.assertRaises(AssertionError):
            _ = ModelHub.new_fromList(models=models, useNamesAsKeys=True)

    def _testModel_reload(self, modelHub: ModelHub, dataDf: pd.DataFrame) -> None:
        dirPath = self.dirPath

        _dirPath = os.path.join(dirPath, 'mmooddeell')
        modelHub.save(dirPath=_dirPath)

        modelHub_alt0 = ModelHub.load(dirPath=_dirPath)
        assert isinstance(modelHub_alt0, ModelHub)
        assert modelHub.name == modelHub_alt0.name
        assert set(modelHub.subModelKeys) == set(modelHub_alt0.subModelKeys)
        assert set(modelHub.attrs) == set(modelHub_alt0.attrs)
        assert modelHub.attrs == modelHub_alt0.attrs

        modelHub_alt1 = ModelHub.load(dirPath=_dirPath, lazyLevel=1)
        assert isinstance(modelHub_alt1, ModelHub)
        assert modelHub.name == modelHub_alt1.name
        assert set(modelHub.subModelKeys) == set(modelHub_alt1.subModelKeys)
        assert set(modelHub.attrs) == set(modelHub_alt1.attrs)
        assert modelHub.attrs == modelHub_alt1.attrs
