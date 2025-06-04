# mypy: disable-error-code="assignment,misc,override"
import os.path
import warnings
from typing import Any, Callable, Mapping

import numpy as np
import pandas as pd
from cachetools import cached

from anre.utils import functions
from anre.utils.modeling.model.iModel import IModel
from anre.utils.modeling.model.iPredictModel import typeX
from anre.utils.modeling.model.modelHub.modelHub import ModelHub
from anre.utils.modeling.model.partitionModel.info import Info
from anre.utils.modeling.transformer.iTransformer import ITransformer
from anre.utils.worker.worker import Worker


class PartitionModel(ModelHub, IModel):
    """Modelis, kuris savyje turi daug instancu tarpusayje analogisku IModel

    Skirtingi instansai apmokyti su skirtingu data subsetu (ismetantn viena konkrecia particija)
    Taigi gaunasi, kad turim modeliu: kiekvienai particiai po viena + oosModel

    visiem trainingcase'am galima suskaiciuoti oos prediction'a.

    Tai modelHub'as, kuris manigina savo modeliu idine logika ir prasitesia i IModel

    """

    __version__ = '0.0.0.1'
    classId: str = Info.get_expectedClassId()
    InfoClass = Info

    @classmethod
    def new_buildFit_fromDataDf(
        cls,
        dataDf: pd.DataFrame,
        buildFitModelFun: Callable,
        partitionSr: pd.Series | None = None,
        partitionField: str | None = None,
        caseField: str | None = None,
        name: str | None = None,
        attrs: dict | None = None,
        worker: Worker | None = None,
        fitKwargs: dict | None = None,
        oosModelKey: str = '__oos__',
    ) -> 'PartitionModel':
        """Builds PartitionModel from DataFrame and buildFitModelFun

        dataDf suskaldomas pagal partitionField, po viena particija ismetama ir taikant buildFitWhModel sukuriami modeliai

        Sukuria modeli, kuris imituoja pradini modeli, bet po vandeniu yra suskaidytas i particijas, kad kiekviena particja gali tureti savo oos prediction'a

        Pasirupina visais cehckais ir suderinamumais (kokius tiksugebejom sugalvoti
        buildFitModelFun: Callable, first argument must be data for fitting (single dataFrame), in addition **kwargs will be passed to it.
        """

        fitKwargs = dict() if fitKwargs is None else fitKwargs
        assert isinstance(fitKwargs, dict)

        assert isinstance(dataDf, pd.DataFrame)
        assert not dataDf.empty

        if partitionSr is None:
            assert partitionField is not None
            assert partitionField in dataDf.columns, f'{partitionField=} is not in dataDf'
            partitionSr = dataDf[partitionField].copy()

        assert not partitionSr.isna().any()
        assert not partitionSr.isnull().any()
        assert pd.api.types.is_object_dtype(partitionSr.dtype)
        assert partitionSr.index.equals(dataDf.index)

        if partitionField is not None:
            assert isinstance(partitionField, str)
            assert partitionField in dataDf.columns, f'{partitionField=} is not in dataDf'
            assert dataDf[partitionField].equals(partitionSr)

        if caseField is not None:
            assert isinstance(caseField, str)
            assert caseField in dataDf.columns, f'{caseField=} is not in dataDf'
            assert not dataDf[caseField].isna().any()
            assert not dataDf[caseField].isnull().any()
            assert pd.api.types.is_integer_dtype(
                dataDf[caseField].dtype
            ) or pd.api.types.is_object_dtype(dataDf[caseField].dtype)

            # test that case -> partition is uniquely defined
            _tdf = pd.concat(
                {'case': dataDf[caseField], 'partition': partitionSr}, axis=1
            ).drop_duplicates()
            assert _tdf['case'].is_unique
            caseMapPartition = _tdf.set_index('case')['partition'].to_dict()
        else:
            caseMapPartition = None

        ### prepare arguments for scale
        partitionSet = set(partitionSr.unique())
        kwargsList = []
        for partition in partitionSet:
            assert isinstance(partition, str), (
                f'partition(`{partition}`) is must be str or int, but got: {type(partition)}'
            )
            _partKwargs = dict(
                buildFitModelFun=buildFitModelFun,
                dataDf=dataDf,
                partitionSr=partitionSr,
                partition=partition,
                fitKwargs=fitKwargs,
            )
            kwargsList.append(_partKwargs)
        # add overall strategy
        assert oosModelKey not in partitionSet
        _partKwargs = dict(
            buildFitModelFun=buildFitModelFun,
            dataDf=dataDf,
            partitionSr=partitionSr,
            partition=oosModelKey,
            fitKwargs=fitKwargs,
        )
        kwargsList.append(_partKwargs)
        del _partKwargs

        ### run scale models
        worker = Worker.new_sequential(show_progress=True) if worker is None else worker
        assert isinstance(worker, Worker)
        subModelKeys = tuple([kw['partition'] for kw in kwargsList])
        _modelList = worker.starmap(fun=cls._buildFit_subModel, kwargs_list=kwargsList)
        modelDict: dict[str, IModel] = {key: model for key, model in zip(subModelKeys, _modelList)}
        del _modelList, kwargsList

        ### create object
        instance = cls.new(
            modelDict=modelDict,
            name=name,
            attrs=attrs,
            subModelKeys=subModelKeys,  # type: ignore[arg-type]
            caseMapPartition=caseMapPartition,
            partitionField=partitionField,
            caseField=caseField,
            oosModelKey=oosModelKey,
        )
        return instance

    @classmethod
    def new(
        cls,
        modelDict: Mapping[str, IModel],
        name: str | None = None,
        attrs: dict | None = None,
        subModelKeys: list[str] | None = None,
        caseMapPartition: dict[int | str, str] | None = None,
        partitionField: str | None = None,
        caseField: str | None = None,
        oosModelKey: str = '__oos__',
        skipValidation=False,
    ) -> 'PartitionModel':
        name = cls.__name__ if name is None else name
        subModelKeys = list(modelDict) if subModelKeys is None else subModelKeys
        caseMapPartition = dict() if caseMapPartition is None else caseMapPartition
        attrs = dict() if attrs is None else attrs

        assert '__caseMapPartition__' not in attrs
        attrs['__caseMapPartition__'] = caseMapPartition
        assert '__partitionField__' not in attrs
        attrs['__partitionField__'] = partitionField
        assert '__caseField__' not in attrs
        attrs['__caseField__'] = caseField
        assert '__oosModelKey__' not in attrs
        attrs['__oosModelKey__'] = oosModelKey

        return cls(
            modelDict=modelDict,
            name=name,
            attrs=attrs,
            subModelKeys=subModelKeys,
            isLazy=False,
            inputTransformer=None,
            outputTransformer=None,
            skipValidation=skipValidation,
        )

    def __init__(
        self,
        modelDict: Mapping[str, IModel | str],
        name: str,
        attrs: dict,
        subModelKeys: list[str],
        isLazy: bool,
        inputTransformer: ITransformer | None,
        outputTransformer: ITransformer | None,
        skipValidation: bool = False,
    ):
        # is pradziunetikrinam, tikrinsime gale
        super().__init__(
            modelDict=modelDict,
            name=name,
            attrs=attrs,
            subModelKeys=subModelKeys,
            isLazy=isLazy,
            inputTransformer=inputTransformer,
            outputTransformer=outputTransformer,
            skipValidation=True,
        )

        # we put constrains, that now _modelDict has IModel, se we need redefine
        self._modelDict: dict[str, IModel | str] = self._checkConvert_subModelsToIModel(
            self._modelDict
        )

        if not skipValidation:
            self.validate()

    def validate(self):
        super().validate()

        ### _oosModel
        assert '__oosModelKey__' in self.attrs
        assert isinstance(self.oosModelKey, str)
        assert self.oosModelKey in self._modelDict
        modelOrPath = self._modelDict[self.oosModelKey]
        if isinstance(modelOrPath, str):
            assert self._isLazy
            assert os.path.exists(modelOrPath)
        else:
            assert isinstance(self.oosModel, IModel)
            assert self.oosModel.isFitted

        ### sub-models
        for partitionId, model in self._modelDict.items():
            assert isinstance(partitionId, str)
            if isinstance(model, str):
                assert self._isLazy
                assert os.path.exists(model)
            else:
                assert isinstance(model, IModel), (
                    f'strategy(`{model}`) expected to be instance of IModel, but got {type(model)}'
                )
                assert isinstance(model, self.oosModel.__class__)
                xFields_oos = self._get_xFields_fromModel(model=self.oosModel)
                xFields_model = self._get_xFields_fromModel(model=model)
                assert xFields_oos == xFields_model
                assert model.isFitted
                assert model.input_shape == self.oosModel.input_shape
                assert model.output_shape == self.oosModel.output_shape
                assert model.isRegression == self.oosModel.isRegression
                assert model.isClassification == self.oosModel.isClassification

        ### caseMapPartition
        assert '__caseMapPartition__' in self.attrs
        assert isinstance(self._caseMapPartition, dict)
        for caseId, partitionId in self._caseMapPartition.items():
            assert caseId is not None
            assert isinstance(caseId, (int, str))
            assert isinstance(partitionId, str)
            assert partitionId in self._modelDict

        ### partitionField
        assert '__partitionField__' in self.attrs
        assert self.partitionField is None or isinstance(self.partitionField, str)

        ### caseField
        assert '__caseField__' in self.attrs
        assert self.caseField is None or isinstance(self.caseField, str)

    @property
    def _caseMapPartition(self) -> dict[str | int, str]:
        return self.attrs['__caseMapPartition__']

    @property
    def partitionField(self) -> str | None:
        return self.attrs['__partitionField__']

    @property
    def caseField(self) -> str | None:
        return self.attrs['__caseField__']

    @property
    def oosModelKey(self) -> str:
        return self.attrs['__oosModelKey__']

    @property
    def oosModel(self) -> IModel:
        return self.get_subModel(self.oosModelKey)

    @property
    def isFitted(self):
        return self.oosModel.isFitted

    @property
    def output_shape(self):
        return self.oosModel.output_shape

    @property
    def input_shape(self):
        return self.oosModel.input_shape

    @property
    def isRegression(self):
        return self.oosModel.isRegression

    @property
    def isClassification(self):
        return self.oosModel.isClassification

    @cached({})
    def get_xFields(self) -> list[str]:
        return self._get_xFields_fromModel(model=self.oosModel)

    def get_subModel(self, key: str) -> IModel:
        subModel = super().get_subModel(key=key)
        assert isinstance(subModel, IModel)
        return subModel

    def preload_byCaseId(self, caseId: str | int | None):
        partitionId = self._caseMapPartition.get(caseId)  # type: ignore[arg-type]
        backendModel = self._get_backendModel(partitionId=partitionId)
        _ = self._collect_leafModels(backendModel)

    def get_partitionList(self) -> list[str]:
        """All sub-models, but oos"""
        return functions.diff_list(self.subModelKeys, [self.oosModelKey])

    def predict(
        self, X: typeX, forceOosModel: bool = False, caseId: str | int | None = None, **kwargs
    ) -> np.ndarray:
        """

        forceOosModel: if True, do not check any partisions or map to them, just use oos strategy.
        """

        X = self._inputTransformer.transform(X)

        if forceOosModel:
            outputAr = self.oosModel.predict(X=X, **kwargs)
            return self._outputTransformer.inverse_transform(outputAr)

        elif caseId is not None:
            partition = self._caseMapPartition.get(caseId)
            outputAr = self.predict_byPartition(X=X, partitionId=partition, **kwargs)
            return self._outputTransformer.inverse_transform(outputAr)

        elif self.partitionField is not None or self.caseField is not None:
            assert isinstance(X, pd.DataFrame)
            if self.partitionField is not None and self.partitionField in X.columns:
                partitionSr = X[self.partitionField]
            elif self.caseField is not None and self.caseField in X.columns:
                caseSr = X[self.caseField].astype(object)
                partitionSr = pd.Series(
                    [self._caseMapPartition.get(caseId) for caseId in caseSr],
                    index=caseSr.index,
                    dtype=object,
                )
            else:
                msg = f'We expect to see at least one of [partitionField={self.partitionField}, caseField={self.caseField}] in X'
                raise AssertionError(msg)

            assert isinstance(partitionSr, pd.Series)
            assert isinstance(X, pd.DataFrame)
            assert partitionSr.shape[0] == X.shape[0]
            assert partitionSr.index.equals(X.index)
            assert pd.api.types.is_object_dtype(partitionSr.dtype)
            partitionSet = set(partitionSr.unique())
            assert all([
                partition in self._modelDict for partition in partitionSet if partition is not None
            ])

            output_shape = (X.shape[0],) + self.oosModel.output_shape[1:]
            outputAr = np.full(output_shape, np.nan)
            partitionAr = partitionSr.values

            for partition in partitionSet:
                ind = partitionAr == partition
                _localOutputAr = self.predict_byPartition(
                    X=X.loc[ind], partitionId=partition, **kwargs
                )
                assert _localOutputAr.shape[0] == np.sum(ind)
                assert _localOutputAr.shape[1:] == output_shape[1:]
                outputAr[ind] = _localOutputAr

            return self._outputTransformer.inverse_transform(outputAr)

        # Jei jaudaeijom iki cia tai oos, bet davai panervima vartotoja
        msg = 'Using oos strategy. If this is intended act, please use forceOosModel=True'
        warnings.warn(msg, RuntimeWarning)
        outputAr = self.oosModel.predict(X=X, **kwargs)
        return self._outputTransformer.inverse_transform(outputAr)

    def predict_byCase(self, X: typeX, caseId: int | str | None, **kwargs: Any) -> np.ndarray:
        assert isinstance(caseId, (str, int, np.integer)) or caseId is None
        partitionId = self._caseMapPartition.get(caseId, None) if caseId is not None else None
        return self.predict_byPartition(X=X, partitionId=partitionId, **kwargs)

    def predict_byPartition(self, X: typeX, partitionId: str | None, **kwargs) -> np.ndarray:
        assert isinstance(partitionId, (str, int, np.integer)) or partitionId is None
        model = self._get_backendModel(partitionId=partitionId)  # type: ignore[arg-type]
        X = self._inputTransformer.transform(X)
        outputAr = model.predict(X, **kwargs)
        return self._outputTransformer.inverse_transform(outputAr)

    def _get_backendModel(self, partitionId: str | None) -> IModel:
        if partitionId is None:
            return self.oosModel
        else:
            assert partitionId in self._modelDict, (
                f'Unknown partition(`{partitionId}`) provided expecting values in: {list(self._modelDict)}'
            )
            return self.get_subModel(partitionId)

    @staticmethod
    def _buildFit_subModel(
        buildFitModelFun: Callable,
        dataDf: pd.DataFrame,
        partitionSr: pd.Series,
        partition: str,
        fitKwargs: dict,
    ) -> IModel:
        assert isinstance(partition, str)
        assert not partitionSr.isna().any()
        assert not partitionSr.isnull().any()
        assert pd.api.types.is_object_dtype(partitionSr.dtype)
        assert partitionSr.index.equals(dataDf.index)

        ind = ~partitionSr.eq(partition)
        assert ind.any(), f'partition(`{partition}`) do not have any data.'

        _df = dataDf.loc[ind]
        model = buildFitModelFun(_df, **fitKwargs)
        assert isinstance(model, IModel)
        assert model.isFitted

        return model
