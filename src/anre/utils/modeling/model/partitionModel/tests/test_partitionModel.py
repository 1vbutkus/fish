import os
import tempfile
import warnings
from itertools import cycle
from typing import Any

import numpy as np
import pandas as pd

from anre.utils import pandas_ as pdu
from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.leafModel.leafModel import LeafModel
from anre.utils.modeling.model.partitionModel.partitionModel import PartitionModel
from anre.utils.worker.worker import Worker


class TestPartitionModel(testutil.TestCase):
    rootDirPath: str
    partitionField: str
    caseField: str
    hp: dict[str, Any]
    xFields: pd.Index
    yField: str
    dirPath: str
    dataDf: pd.DataFrame

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        rootDirPath = tempfile.mkdtemp()
        dirPath = os.path.join(rootDirPath, 'someDir', 'deeperDir')

        caseField = '_case'
        partitionField = '_partition'
        hp = {
            'min_child_samples': 2,
            'n_estimators': 10,
            'n_jobs': 1,
        }

        dataDf = pdu.new.get_randomDf(shape=(26, 3))
        yField = dataDf.columns[0]
        xFields = dataDf.columns[1:]
        cases = dataDf[caseField] = list(range(dataDf.shape[0] // 2)) * 2
        caseMapPartition = {case: partition for case, partition in zip(cases, cycle(range(3)))}
        dataDf[partitionField] = [str(caseMapPartition[case]) for case in cases]

        cls.dataDf = dataDf
        cls.hp = hp
        cls.yField = yField
        cls.xFields = xFields
        cls.caseField = caseField
        cls.partitionField = partitionField
        cls.rootDirPath = rootDirPath
        cls.dirPath = dirPath

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        FileSystem.delete_folder(path=cls.rootDirPath, ignore_errors=True)
        assert not os.path.exists(cls.rootDirPath)

    def test_new_buildFit_fromDataDf(self) -> None:
        dataDf = self.dataDf.copy()
        hp = self.hp
        xFields = self.xFields
        yField = self.yField
        partitionField = self.partitionField
        caseField = self.caseField

        def buildFitModelFun(df: pd.DataFrame, **hp):
            assert isinstance(df, pd.DataFrame)
            model = LeafModel.new_lgbmRegression(**hp)
            model.fit(df[xFields], df[yField])
            return model

        worker = Worker.new_sequential(show_progress=False)
        partitionModel = PartitionModel.new_buildFit_fromDataDf(
            dataDf=dataDf,
            buildFitModelFun=buildFitModelFun,
            partitionField=partitionField,
            caseField=caseField,
            worker=worker,
            fitKwargs=hp,
        )
        self._testModel_usingData(partitionModel=partitionModel, dataDf=dataDf)
        predOos = partitionModel.predict(X=dataDf, forceOosModel=True)

        # lets try to fit in scale
        worker = Worker.new_joblib()
        partitionModel_scaled = PartitionModel.new_buildFit_fromDataDf(
            dataDf=dataDf,
            buildFitModelFun=buildFitModelFun,
            partitionField=partitionField,
            caseField=caseField,
            worker=worker,
            fitKwargs=hp,
        )
        self._testModel_usingData(partitionModel=partitionModel_scaled, dataDf=dataDf)
        predOos_scaled = partitionModel_scaled.predict(X=dataDf, forceOosModel=True)
        assert np.all(predOos_scaled == predOos)

        ### twike df
        partitionSr = dataDf.pop(partitionField)
        caseSr = dataDf.pop(caseField)
        # still OK
        resAr5 = partitionModel.predict(X=dataDf, forceOosModel=True)
        assert np.all(resAr5 == predOos)
        # not Ok any more, it expects partitionField or caseField in X
        with self.assertRaises(AssertionError):
            _ = partitionModel.predict(X=dataDf)

        ### recreate without partision link
        dataDf[caseField] = caseSr
        partitionModel = PartitionModel.new_buildFit_fromDataDf(
            dataDf=dataDf,
            buildFitModelFun=buildFitModelFun,
            partitionSr=partitionSr,
            caseField=caseField,
            worker=Worker.new_sequential(show_progress=False),
            fitKwargs=hp,
        )
        self._testModel_usingData(partitionModel=partitionModel, dataDf=dataDf)
        predOos = partitionModel.predict(X=dataDf, forceOosModel=True)

        ### twike df
        # make unknown case
        dataDf.loc[0, caseField] = -99
        resAr6 = partitionModel.predict(X=dataDf)
        assert resAr6[0] == predOos[0]

        # case with no link to case or partition
        partitionModel = PartitionModel.new_buildFit_fromDataDf(
            dataDf=dataDf,
            buildFitModelFun=buildFitModelFun,
            partitionSr=partitionSr,
            worker=Worker.new_sequential(show_progress=False),
            fitKwargs=hp,
        )
        predOos = partitionModel.predict(X=dataDf, forceOosModel=True)
        with self.assertWarns(RuntimeWarning):
            predOos2 = partitionModel.predict(X=dataDf)
        assert np.all(predOos2 == predOos)

    def _testModel_usingData(self, partitionModel: PartitionModel, dataDf: pd.DataFrame):
        self._testModel_predict(partitionModel=partitionModel, dataDf=dataDf)
        self._testModel_reload(partitionModel=partitionModel, dataDf=dataDf)

    def _testModel_predict(self, partitionModel: PartitionModel, dataDf: pd.DataFrame):
        partitionField = self.partitionField
        caseField = self.caseField

        dataDf = dataDf.copy()

        assert isinstance(partitionModel, PartitionModel)

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            resAr1 = partitionModel.predict(X=dataDf)

        assert isinstance(resAr1, np.ndarray)
        assert resAr1.shape[0] == dataDf.shape[0]

        # partitionModel.predict_byPartition(X=dataDf, partitionId='1')
        # partitionModel.predict_byPartition(X=dataDf, partitionId=None)

        # oos by definitions
        resAr2 = partitionModel.predict(X=dataDf, forceOosModel=True)
        assert not np.all(resAr2 == resAr1)

        # still oos
        resAr3 = partitionModel.predict_byPartition(X=dataDf, partitionId=None)
        assert np.all(resAr2 == resAr3)

        ### particular partition
        # not oos any more
        partitionId = partitionModel.get_partitionList()[0]
        resAr4 = partitionModel.predict_byPartition(X=dataDf, partitionId=partitionId)
        assert not np.all(resAr4 == resAr3)

        # for known cases it automaticly maped to correct partition
        if partitionField in dataDf:
            ind = dataDf[partitionField] == partitionId
            sdf = dataDf.loc[ind]
            _resAr_sub1 = partitionModel.predict(X=sdf)
            _resAr_sub2 = partitionModel.predict_byPartition(X=sdf, partitionId=partitionId)
            assert np.all(_resAr_sub1 == _resAr_sub2)
            _resAr_sub3_oos = partitionModel.predict_byPartition(X=sdf, partitionId=None)
            assert not np.all(_resAr_sub3_oos == _resAr_sub2)

        ### particular caseId
        # not oos any more
        caseId = dataDf[caseField].iloc[0]
        resAr5 = partitionModel.predict_byCase(X=dataDf, caseId=caseId)
        assert not np.all(resAr5 == resAr3)

        # for known cases it automaticly maped to correct caseId
        ind = dataDf[caseField] == caseId
        sdf = dataDf.loc[ind]
        _resAr_sub1 = partitionModel.predict(X=sdf)
        assert _resAr_sub1 is not None
        _resAr_sub2 = partitionModel.predict_byCase(X=sdf, caseId=caseId)
        assert np.all(_resAr_sub1 == _resAr_sub2)
        _resAr_sub3_oos = partitionModel.predict_byCase(X=sdf, caseId=None)
        assert not np.all(_resAr_sub3_oos == _resAr_sub2)

    def _testModel_reload(self, partitionModel: PartitionModel, dataDf: pd.DataFrame):
        dirPath = self.dirPath

        _dirPath = os.path.join(dirPath, 'mmooddeell')
        partitionModel.save(dirPath=_dirPath)

        model2 = PartitionModel.load(dirPath=_dirPath)
        assert isinstance(model2, PartitionModel)

        pred1 = partitionModel.predict(dataDf)
        pred2 = model2.predict(dataDf)
        assert np.all(pred2 == pred1)

        FileSystem.delete_folder(_dirPath)
