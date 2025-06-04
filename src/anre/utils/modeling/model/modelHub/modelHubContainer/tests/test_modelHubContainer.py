import os
import tempfile
from typing import Any

import pytest

from anre.utils import pandas_ as pdu
from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.leafModel.leafModel import LeafModel
from anre.utils.modeling.model.modelHub.modelHub import ModelHub
from anre.utils.modeling.model.modelHub.modelHubContainer.modelHubContainer import ModelHubContainer


@pytest.mark.slow
class TestModelHubContainer(testutil.TestCase):
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
        dirPath = self.dirPath

        ### create sub-models
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

        # create ModelHub
        modelDict = dict(model0=model0, model1=model1)
        modelHub0 = ModelHub.new(modelDict=modelDict)
        modelHubContainer = ModelHubContainer(modelHub=modelHub0)
        assert isinstance(modelHubContainer, ModelHubContainer)

        _dirPath = os.path.join(dirPath, 'modelHubContainer')
        modelHubContainer.save(dirPath=_dirPath)

        modelHubContainer_alt = ModelHubContainer.load(dirPath=_dirPath)
        assert isinstance(modelHubContainer_alt, ModelHubContainer)
