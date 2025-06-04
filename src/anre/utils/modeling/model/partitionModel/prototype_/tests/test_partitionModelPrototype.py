import os
import tempfile
from itertools import cycle
from typing import Any

import numpy as np
import pandas as pd
import pytest

from anre.utils import pandas_ as pdu
from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.leafModel.leafModel import LeafModel
from anre.utils.modeling.model.partitionModel.prototype_.partitionModel import PartitionModel


@pytest.mark.slow
class TestPartitionModelPrototype(testutil.TestCase):
    dirPath: str
    rootDirPath: str

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

    def test_happyPath(self) -> None:
        dirPath = self.dirPath

        cases = [f'c{i}' for i in range(15)]
        partitions = [0, 1, 3]
        case2dataDict = {case: pdu.new.get_randomDf(shape=(15, 3)) for case in cases}

        case2PartitionDict = {case: partition for case, partition in zip(cases, cycle(partitions))}

        def buildFitWhMode(cases, **hp):
            _dataList = [case2dataDict[case] for case in cases]
            df = pd.concat(_dataList)
            yField = df.columns[0]
            xFields = df.columns[1:]

            model = LeafModel.new_lgbmRegression(**hp)
            model.fit(df[xFields], df[yField])

            return model

        hp: dict[str, Any] = {
            'min_child_samples': 2,
            'n_estimators': 10,
        }
        partitionModel = PartitionModel.new_buildFit(
            buildFitWhModel=buildFitWhMode,
            case2PartitionDict=case2PartitionDict,  # type: ignore[arg-type]
            **hp,  # type: ignore[arg-type]
        )
        assert isinstance(partitionModel, PartitionModel)

        caseId = 'c14'
        df = case2dataDict[caseId]

        pred1 = partitionModel.predict(X=df, caseId=caseId)
        pred2 = partitionModel.predict(X=df, caseId=None)
        assert np.max(np.abs(pred1 - pred2)) > 1e-7

        filePath = os.path.join(dirPath, 'strategy.pkl')
        partitionModel.save(filePath)
        partitionModel_alt = PartitionModel.load(filePath)
        assert isinstance(partitionModel_alt, PartitionModel)
        assert partitionModel is not partitionModel_alt

        pred1_alt = partitionModel_alt.predict(X=df, caseId=caseId)
        pred2_alt = partitionModel_alt.predict(X=df, caseId=None)
        assert np.max(np.abs(pred1 - pred1_alt)) < 1e-7
        assert np.max(np.abs(pred2 - pred2_alt)) < 1e-7
