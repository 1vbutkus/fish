# mypy: disable-error-code="var-annotated"
from __future__ import annotations

import os
import os.path
from typing import Any, Callable

import numpy as np
import pandas as pd
from frozendict import frozendict

from anre.utils import functions, saveobj
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.iPredictModel import IPredictModel, typeX
from anre.utils.worker.worker import Worker


class PartitionModel(IPredictModel):
    """Modelis, kuris savyje turi daug instancu analogisku IPredictModel

    Skirtingi instansai apmokyti su skirtingu subsetu (ismetantn viena konkrecia particija)
    Taigi gaunasi, kad turim modeliu: kiekvienai particiai po viena + oosModel

    visiem trainingcase'am galima suskaiciuoti oos prediction'a.
    """

    @classmethod
    def new_buildFit(
        cls,
        buildFitWhModel: Callable,
        case2PartitionDict: dict[str | int, str | int],
        showProgress: bool = False,
        **kwargs,
    ):
        """

        :param buildFitWhModel:
        :param case2PartitionDict:
        :param showProgress:
        :param kwargs: papildomi kintamieji siunciami i buildFitWhMode
        :return:
        """

        assert callable(buildFitWhModel)
        assert isinstance(case2PartitionDict, (dict, frozendict))

        partition2CaseListDict = functions.groupByList(
            case2PartitionDict.keys(), case2PartitionDict.values()
        )
        _values = functions.flattenList(list(partition2CaseListDict.values()))
        partition2CaseListDict_fitDict = {
            key: functions.diff_list(_values, valList)
            for key, valList in partition2CaseListDict.items()
        }
        assert '__all__' not in partition2CaseListDict_fitDict
        partition2CaseListDict_fitDict['__all__'] = _values

        worker = Worker.new_sequential(show_progress=showProgress)
        _keys = partition2CaseListDict_fitDict.keys()
        argsTupleList = [(partition2CaseListDict_fitDict[key],) for key in _keys]
        _whModelList = worker.starmap(buildFitWhModel, args_tuple_list=argsTupleList, **kwargs)
        partition2whModelDict = {key: whMode for key, whMode in zip(_keys, _whModelList)}

        fitReport = {}
        oosModel = partition2whModelDict.pop('__all__')
        partitionModel = cls(
            oosModel=oosModel,
            partition2modelDict=partition2whModelDict,
            case2partitionDict=case2PartitionDict,
            fitReport=fitReport,
        )
        return partitionModel

    def __init__(
        self,
        oosModel: IPredictModel,
        partition2modelDict: dict[int | str, IPredictModel],
        case2partitionDict: dict[int | str, int | str],
        fitReport: dict,
    ):
        assert isinstance(oosModel, IPredictModel)
        assert isinstance(partition2modelDict, (dict, frozendict))
        assert isinstance(case2partitionDict, (dict, frozendict))
        assert isinstance(fitReport, (dict, frozendict))

        self._oosModel: IPredictModel = oosModel
        self._partition2modelDict: frozendict[int | str, IPredictModel] = frozendict(
            partition2modelDict
        )
        self._case2partitionDict: frozendict[int | str, int | str] = frozendict(case2partitionDict)
        self._fitReport: frozendict = frozendict(fitReport)

        self.validate()

    def validate(self):
        ### _oosModel
        assert isinstance(self._oosModel, IPredictModel)

        ### _partitionModelDict
        assert isinstance(self._partition2modelDict, (dict, frozendict))
        for partitionId, model in self._partition2modelDict.items():
            assert isinstance(model, IPredictModel)
            assert isinstance(partitionId, (int, str))

        ### _caseIdDict
        assert isinstance(self._case2partitionDict, (dict, frozendict))
        for caseId, partitionId in self._case2partitionDict.items():
            assert isinstance(caseId, (int, str))
            assert isinstance(partitionId, (int, str))
            assert partitionId in self._partition2modelDict

        ### _fitReport
        assert isinstance(self._fitReport, (dict, frozendict))

    @property
    def fitReport(self) -> dict:
        return dict(self._fitReport)

    @property
    def oosModel(self) -> IPredictModel:
        return self._oosModel

    def predict(self, X: typeX, caseId: str | None = None, **kwargs: Any) -> np.ndarray:
        partitionId = self._case2partitionDict.get(caseId, None)  # type: ignore[arg-type]
        return self.predict_byPartition(X=X, partitionId=partitionId)

    def get_predictDf(self, X: typeX, caseIds: list[str | int]) -> pd.DataFrame:
        """The same X on different cases

        Equivalent (but faster): pd.concat([predict(X=X, caseId=CaseId for caseId in caseIds], axis=1)

        """

        partitionDict = {caseId: self._case2partitionDict.get(caseId, None) for caseId in caseIds}
        _partitions = list(set(partitionDict.values()))

        _predDict_byPartition = {
            partitionId: self.predict_byPartition(X, partitionId=partitionId)
            for partitionId in _partitions
        }
        if hasattr(X, 'index'):
            index = X.index
        else:
            index = pd.Index(range(X.shape[0]))
        _srDict = {
            caseId: pd.Series(_predDict_byPartition[partition], index=index, name=caseId)
            for caseId, partition in partitionDict.items()
        }
        predictDf = pd.concat(_srDict, axis=1)
        return predictDf

    def predict_byPartition(self, X: typeX, partitionId: int | str | None) -> np.ndarray:
        model = self._get_backendModel(partitionId=partitionId)
        return model.predict(X)

    def get_partitionList(self) -> list[int | str]:
        return list(self._partition2modelDict)

    def _get_backendModel(self, partitionId: int | str | None) -> IPredictModel:
        if partitionId is None:
            return self._oosModel
        else:
            return self._partition2modelDict[partitionId]

    def save(self, filePath: str, overwrite: bool = False):
        assert overwrite or not os.path.exists(filePath)
        dirPath = os.path.dirname(filePath)
        FileSystem.create_folder(dirPath, recreate=False)
        saveobj.dump(self, path=filePath, overwrite=overwrite)
        return True

    @classmethod
    def load(cls, filePath: str) -> PartitionModel:
        assert os.path.exists(filePath), f'Model filePath does not exist: {filePath}'
        loadInstance = saveobj.load(path=filePath)
        assert isinstance(loadInstance, cls)
        loadInstance.validate()
        return loadInstance
