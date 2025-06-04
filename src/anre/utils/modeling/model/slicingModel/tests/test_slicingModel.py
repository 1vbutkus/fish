import os
import tempfile
import warnings
from typing import Any

import numpy as np
import pandas as pd

from anre.utils import functions, testutil
from anre.utils import pandas_ as pdu
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.leafModel.leafModel import LeafModel
from anre.utils.modeling.model.slicingModel.slicingModel import SlicingModel
from anre.utils.modeling.timeSlice.timeSlice import TimeSlice
from anre.utils.modeling.timeSlice.timeSliceSchema import TimeSliceSchema


class TestSlicingModel(testutil.TestCase):
    rootDirPath: str
    dataDf: pd.DataFrame
    hp: dict[str, Any]
    caseField: str
    dirPath: str
    rootTimeSlice: TimeSlice
    yField: str
    xFields: pd.Index

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        rootDirPath = tempfile.mkdtemp()
        dirPath = os.path.join(rootDirPath, 'someDir', 'deeperDir')

        caseField = '_case'
        hp = {
            'min_child_samples': 2,
            'n_estimators': 10,
            'n_jobs': 1,
        }

        dataDf = pdu.new.get_randomDf(shape=(52, 3))
        yField = dataDf.columns[0]
        xFields = dataDf.columns[1:]
        dataDf[caseField] = list(range(dataDf.shape[0] // 2)) * 2
        dataDf[caseField] = dataDf[caseField].astype(str)

        values = list(dataDf[caseField].unique())
        params = {
            'trainSizeDefault': 5,
            'testSizeDefault': 2,
            'levels': [
                {'shiftStep': 5},
            ],
        }
        timeSliceSchema = TimeSliceSchema(values=values, prm=params)
        rootTimeSlice = timeSliceSchema.get_rootTimeSlice()

        cls.dataDf = dataDf
        cls.hp = hp
        cls.yField = yField
        cls.xFields = xFields
        cls.caseField = caseField
        cls.rootDirPath = rootDirPath
        cls.dirPath = dirPath
        cls.rootTimeSlice = rootTimeSlice

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        FileSystem.delete_folder(path=cls.rootDirPath, ignore_errors=True)
        assert not os.path.exists(cls.rootDirPath)

    def test_new_manual(self) -> None:
        dataDf = self.dataDf.copy()
        hp = self.hp
        xFields = self.xFields
        yField = self.yField
        caseField = self.caseField

        def buildFitModelFun(df: pd.DataFrame, **hp):
            assert isinstance(df, pd.DataFrame)
            model = LeafModel.new_lgbmRegression(**hp)
            model.fit(df[xFields], df[yField])
            return model

        modelDict = dict()
        modelMapTrainCases = dict()
        modelMapTestCases = dict()
        cases = list(dataDf[caseField].unique())
        for sliceId in range(1, len(cases) - 1):
            testCases = cases[sliceId : (sliceId + 2)]
            trainCases = functions.diff_list(cases, testCases)[:7]
            ind = dataDf[caseField].isin(trainCases)
            df = dataDf.loc[ind.values]  # type: ignore[index]
            modelKey = min(testCases)
            modelDict[modelKey] = buildFitModelFun(df=df, **hp)
            modelMapTrainCases[modelKey] = trainCases
            modelMapTestCases[modelKey] = testCases

        slicingModel = SlicingModel.new(
            modelDict=modelDict,
            oosModelKey=max(modelDict),
            modelMapTrainCases=modelMapTrainCases,
            modelMapTestCases=modelMapTestCases,
            caseField=caseField,
        )

        self._testModel_usingData(slicingModel=slicingModel, dataDf=dataDf)

    def test_new_buildFit(self) -> None:
        dataDf = self.dataDf.copy()
        hp = self.hp
        xFields = self.xFields
        yField = self.yField
        caseField = self.caseField

        targetSr = dataDf[yField]
        model = LeafModel.new_lgbmRegression(xFields=xFields, verbose=-1, **hp)

        case_sr = pd.Series(dataDf[caseField].unique())
        gr_sr = (pd.Series(range(len(case_sr)), index=case_sr.index) % 3).astype(str)
        modelMapTestCases = case_sr.groupby(gr_sr).apply(list).to_dict()
        modelMapTrainCases = {
            key: functions.diff_list(case_sr, testCases)
            for key, testCases in modelMapTestCases.items()
        }

        slicingModel = SlicingModel.new_buildFit(
            inputDf=dataDf,
            targetSr=targetSr,
            caseField=caseField,
            model=model,
            modelMapTestCases=modelMapTestCases,
            modelMapTrainCases=modelMapTrainCases,
        )

        self._testModel_usingData(slicingModel=slicingModel, dataDf=dataDf)

    def test_new_buildFit_timeSlice(self) -> None:
        dataDf = self.dataDf.copy()
        hp = self.hp
        xFields = self.xFields
        yField = self.yField
        caseField = self.caseField
        rootTimeSlice = self.rootTimeSlice

        targetSr = dataDf[yField]
        model = LeafModel.new_lgbmRegression(xFields=xFields, **hp)

        slicingModel = SlicingModel.new_buildFit_timeSlice(
            inputDf=dataDf,
            targetSr=targetSr,
            caseField=caseField,
            timeSlice=rootTimeSlice,
            model=model,
        )
        self._testModel_usingData(slicingModel=slicingModel, dataDf=dataDf)

    def _testModel_usingData(self, slicingModel: SlicingModel, dataDf: pd.DataFrame):
        self._testModel_predict(slicingModel=slicingModel, dataDf=dataDf)
        self._testModel_reload(slicingModel=slicingModel, dataDf=dataDf)

    def _testModel_predict(self, slicingModel: SlicingModel, dataDf: pd.DataFrame):
        dataDf = dataDf.copy()

        assert isinstance(slicingModel, SlicingModel)

        with self.assertRaises(AssertionError):
            _ = slicingModel.predict(X=dataDf)

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            resAr0 = slicingModel.predict(X=dataDf, skipCheck=True)
            assert isinstance(resAr0, np.ndarray)
            assert resAr0.shape[0] == dataDf.shape[0]
            assert not np.any(pd.isna(resAr0))

        # oos by definitions
        resAr1 = slicingModel.predict_oos(X=dataDf)
        assert np.all(resAr1 == resAr0)

        # pseudoOos
        resAr2 = slicingModel.predict_pseudoOos(X=dataDf)
        assert isinstance(resAr2, np.ndarray)
        assert resAr2.shape[0] == dataDf.shape[0]

    def _testModel_reload(self, slicingModel: SlicingModel, dataDf: pd.DataFrame):
        dirPath = self.dirPath

        _dirPath = os.path.join(dirPath, 'mmooddeell')
        slicingModel.save(dirPath=_dirPath)

        model2 = SlicingModel.load(dirPath=_dirPath)
        assert isinstance(model2, SlicingModel)

        pred1 = slicingModel.predict(dataDf, skipCheck=True)
        pred2 = model2.predict(dataDf, skipCheck=True)
        assert np.all(pred2 == pred1)

        pred1 = slicingModel.predict_pseudoOos(dataDf)
        pred2 = model2.predict_pseudoOos(dataDf)
        assert pd.Series(pred1).equals(pd.Series(pred2))

        FileSystem.delete_folder(_dirPath)
