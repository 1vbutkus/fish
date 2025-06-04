# mypy: disable-error-code="assignment,misc,override,union-attr"
import datetime
import numbers
import os.path
from typing import Any, Mapping

import numpy as np
import pandas as pd
from cachetools import cached
from sklearn.model_selection import KFold

from anre.utils import functions
from anre.utils.modeling.model.iModel import IModel
from anre.utils.modeling.model.iPredictModel import typeX
from anre.utils.modeling.model.leafModel.leafModel import LeafModel
from anre.utils.modeling.model.modelHub.modelHub import ModelHub
from anre.utils.modeling.model.slicingModel.info import Info
from anre.utils.modeling.timeSlice.timeSlice import TimeSlice
from anre.utils.modeling.transformer.iTransformer import ITransformer
from anre.utils.worker.worker import Worker


class SlicingModel(ModelHub, IModel):
    """Modelis, kuris savyje turi daug instancu tarpusayje analogisku IModel

    Skirtingi instansai apmokyti su slenkanciu laiko langu
    """

    __version__ = '0.0.0.1'
    classId: str = Info.get_expectedClassId()
    InfoClass = Info

    @classmethod
    def new_buildFit(
        cls,
        inputDf: pd.DataFrame,
        targetSr: pd.Series,
        caseField: str,
        modelMapTrainCases: dict[str, list[str]],
        modelMapTestCases: dict[str, list[str]],
        model: LeafModel,
        oosModelKey: str | None = None,
        fitKwargs: dict[str, Any] | None = None,
        name: str | None = None,
        worker: Worker | None = None,
    ) -> 'SlicingModel':
        worker = Worker.new_sequential() if worker is None else worker
        fitKwargs = dict() if fitKwargs is None else fitKwargs

        assert isinstance(inputDf, pd.DataFrame)
        assert isinstance(targetSr, pd.Series)
        assert isinstance(caseField, str)
        assert isinstance(modelMapTrainCases, dict)
        assert isinstance(modelMapTestCases, dict)
        assert isinstance(fitKwargs, dict)
        assert oosModelKey is None or isinstance(oosModelKey, str)
        assert set(modelMapTestCases) == set(modelMapTrainCases)

        modelMapTestCases = modelMapTestCases.copy()
        modelMapTrainCases = modelMapTrainCases.copy()
        modelKeys = list(modelMapTestCases)

        kwargs_list = []
        modelKey = None
        for modelKey in modelKeys:
            assert isinstance(modelKey, str)
            trainCases = modelMapTrainCases[modelKey]
            testCases = modelMapTestCases[modelKey]
            assert not set(trainCases) & set(testCases), (
                f'Test and train intersect: {set(trainCases) & set(testCases)}'
            )
            kwargs = {
                'trainCases': trainCases,
            }
            kwargs_list.append(kwargs)
            modelMapTrainCases[modelKey] = [el.__str__() for el in modelMapTrainCases[modelKey]]
            modelMapTestCases[modelKey] = [el.__str__() for el in modelMapTestCases[modelKey]]

        if oosModelKey is None:
            assert modelKey is not None
            oosModelKey = modelKey

        model_list = worker.starmap(
            cls._fit_single_submodel,
            kwargs_list=kwargs_list,
            inputDf=inputDf,
            targetSr=targetSr,
            caseField=caseField,
            model=model,
            fitKwargs=fitKwargs,
        )
        # assert all([isinstance(model, LeafModel) for model in model_list])
        model_dict = {key: model for key, model in zip(modelKeys, model_list)}

        slicing_model = cls.new(
            modelDict=model_dict,
            name=name,
            oosModelKey=oosModelKey,
            modelMapTrainCases=modelMapTrainCases,
            modelMapTestCases=modelMapTestCases,
            caseField=caseField,
        )
        return slicing_model

    @classmethod
    def new_buildFit_timeSlice(
        cls,
        inputDf: pd.DataFrame,
        targetSr: pd.Series,
        caseField: str,
        timeSlice: TimeSlice,
        model: LeafModel,
        fitKwargs: dict[str, Any] | None = None,
        name: str | None = None,
        worker: Worker | None = None,
    ) -> 'SlicingModel':
        modelMapTrainCases = {}
        modelMapTestCases = {}
        modelKey = None
        assert timeSlice.childrenList is not None
        for children_time_slice in timeSlice.childrenList:
            trainCases = children_time_slice.get_trainValues()
            testCases = [el for el in children_time_slice.get_testValues() if el]
            if not testCases:
                break
            testCaseMin = min(testCases)
            modelKey = testCaseMin.__str__()
            modelMapTrainCases[modelKey] = trainCases
            modelMapTestCases[modelKey] = testCases

        assert modelKey is not None
        oosModelKey = modelKey

        return cls.new_buildFit(
            inputDf=inputDf,
            targetSr=targetSr,
            caseField=caseField,
            modelMapTrainCases=modelMapTrainCases,
            modelMapTestCases=modelMapTestCases,
            fitKwargs=fitKwargs,
            name=name,
            worker=worker,
            oosModelKey=oosModelKey,
            model=model,
        )

    @classmethod
    def new_buildFit_cv(
        cls,
        inputDf: pd.DataFrame,
        targetSr: pd.Series,
        caseField: str,
        model: LeafModel,
        fitKwargs: dict[str, Any] | None = None,
        name: str | None = None,
        worker: Worker | None = None,
        cv: int | KFold = 5,
    ) -> 'SlicingModel':
        if isinstance(cv, numbers.Number):
            cv = KFold(n_splits=cv)
        assert isinstance(cv, KFold)
        assert cv.n_splits > 1

        assert caseField in inputDf.columns
        case_sr = inputDf[caseField].drop_duplicates()

        modelMapTrainCases = {}
        modelMapTestCases = {}
        for i, (train_index, test_index) in enumerate(cv.split(X=case_sr)):
            modelMapTrainCases[str(i)] = list(case_sr.iloc[train_index])
            modelMapTestCases[str(i)] = list(case_sr.iloc[test_index])

        oosModelKey = max(modelMapTestCases)

        return cls.new_buildFit(
            inputDf=inputDf,
            targetSr=targetSr,
            caseField=caseField,
            modelMapTrainCases=modelMapTrainCases,
            modelMapTestCases=modelMapTestCases,
            fitKwargs=fitKwargs,
            name=name,
            worker=worker,
            oosModelKey=oosModelKey,
            model=model,
        )

    @classmethod
    def new(
        cls,
        modelDict: dict[str, IModel],
        name: str | None = None,
        attrs: dict | None = None,
        subModelKeys: list[str] | None = None,
        oosModelKey: str | None = None,
        modelMapTrainCases: dict[str, list[str]] | None = None,
        modelMapTestCases: dict[str, list[str]] | None = None,
        caseField: str | None = None,
        skipValidation=False,
        **kwargs,
    ) -> 'SlicingModel':
        assert not kwargs, f'Got unexpected kwargs: {list(kwargs)}'
        name = cls.__name__ if name is None else name
        if subModelKeys is None:
            subModelKeys = list(modelDict)
            subModelKeys.sort()

        oosModelKey = max(subModelKeys) if oosModelKey is None else oosModelKey
        assert isinstance(oosModelKey, str)
        assert oosModelKey in oosModelKey
        attrs = dict() if attrs is None else attrs

        assert '__modelMapTrainCase__' not in attrs
        attrs['__modelMapTrainCases__'] = modelMapTrainCases
        assert '__modelMapTestCases__' not in attrs
        attrs['__modelMapTestCases__'] = modelMapTestCases
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
        # is pradziu netikrinam, tikrinsime gale
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

        # we put constrains, that now _modelDict has IModel, so we need redefine
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

        ### model map case
        assert '__modelMapTrainCases__' in self.attrs
        assert '__modelMapTestCases__' in self.attrs
        assert isinstance(self._modelMapTrainCases, dict)
        assert isinstance(self._modelMapTestCases, dict)
        assert set(self._modelMapTrainCases) == set(self._modelDict)
        assert set(self._modelMapTestCases) == set(self._modelDict)
        for modelKey in self._modelDict:
            trainCases = self._modelMapTrainCases[modelKey]
            testCases = self._modelMapTestCases[modelKey]
            assert not set(trainCases) & set(testCases)
            assert all([isinstance(case, str) for case in trainCases])
            assert all([isinstance(case, str) for case in testCases])

        ### caseField
        assert '__caseField__' in self.attrs
        assert self.caseField is None or isinstance(self.caseField, str)

    @property
    def _modelMapTrainCases(self) -> dict[str, list[str]]:
        return self.attrs['__modelMapTrainCases__']

    @property
    def _modelMapTestCases(self) -> dict[str, list[str]]:
        return self.attrs['__modelMapTestCases__']

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
    def isFitted(self) -> bool:
        return self.oosModel.isFitted

    @property
    def output_shape(self) -> tuple[int | None, ...]:
        return self.oosModel.output_shape

    @property
    def input_shape(self) -> tuple[int | None, ...]:
        return self.oosModel.input_shape

    @property
    def isRegression(self) -> bool:
        return self.oosModel.isRegression

    @property
    def isClassification(self) -> bool:
        return self.oosModel.isClassification

    @cached({})
    def get_xFields(self) -> list[str]:
        return self._get_xFields_fromModel(model=self.oosModel)

    def get_subModel(self, key: str) -> IModel:
        subModel = super().get_subModel(key=key)
        assert isinstance(subModel, IModel)
        return subModel

    def predict_byModel(self, X: typeX, modelKey: str, **kwargs: Any) -> np.ndarray:
        assert isinstance(modelKey, str)
        model = self.get_subModel(key=modelKey)
        X = self._inputTransformer.transform(X)
        outputAr = model.predict(X, **kwargs)
        return self._outputTransformer.inverse_transform(outputAr)

    def predict_byModels(self, X: typeX, modelKeySr: pd.Series, **kwargs: Any) -> np.ndarray:
        """
        Jei modelKeySr turi nan, tai bus rezultate nan

        """

        assert isinstance(modelKeySr, pd.Series)
        assert isinstance(X, pd.DataFrame)
        assert modelKeySr.shape[0] == X.shape[0]
        assert modelKeySr.index.equals(X.index)
        assert pd.api.types.is_object_dtype(modelKeySr.dtype)
        modelKeySet = set(modelKeySr.dropna().unique())
        assert all([modelKey in self._modelDict for modelKey in modelKeySet])

        output_shape = (X.shape[0],) + self.oosModel.output_shape[1:]
        outputAr = np.full(output_shape, np.nan)  # type: ignore[arg-type]
        modelKeyAr = modelKeySr.values

        for modelKey in modelKeySet:
            ind = modelKeyAr == modelKey
            _localOutputAr = self.predict_byModel(X=X.loc[ind], modelKey=modelKey, **kwargs)
            assert _localOutputAr.shape[0] == np.sum(ind)
            assert _localOutputAr.shape[1:] == output_shape[1:]
            outputAr[ind] = _localOutputAr

        return outputAr

    def predict_oos(self, X: typeX, **kwargs: Any) -> np.ndarray:
        return self.predict_byModel(X=X, modelKey=self.oosModelKey, **kwargs)

    def get_modelKeySr(
        self,
        caseSr: pd.Series,
        model_idx: int = 0,
        fit_subset: str = 'test',
        idx_match_type: str = 'exact',
    ) -> pd.Series:
        """ """

        caseMapModelSr: pd.Series = self.get_caseMapModelSr(
            fit_subset=fit_subset, model_idx=model_idx, idx_match_type=idx_match_type
        )

        # map case to model
        if pd.api.types.is_string_dtype(caseSr):
            modelKeySr = caseSr.map(caseMapModelSr)
        elif pd.api.types.is_object_dtype(caseSr):
            idx = caseSr.first_valid_index()
            assert idx is not None, 'No valid cases in caseSr. WTF?'
            elem = caseSr.loc[idx]
            if isinstance(elem, pd.Series):
                elem = elem.iloc[0]
            if isinstance(elem, datetime.date):
                caseMapModelSr.index = (
                    caseMapModelSr.index.to_series().astype('datetime64[ns]').dt.date.values
                )
                modelKeySr = caseSr.map(caseMapModelSr)
            else:
                raise TypeError(f'caseSr must be str or datetime.date, but got {type(elem)}.')
        else:
            raise TypeError('caseSr must be str or datetime.date.')

        return modelKeySr

    def predict_pseudoOos(self, X: typeX, model_idx: int = 0, **kwargs: Any) -> np.ndarray:
        """ """
        assert isinstance(X, pd.DataFrame)
        assert self.caseField is not None
        assert self.caseField in X.columns
        caseSr: pd.Series = X[self.caseField]

        modelKeySr = self.get_modelKeySr(
            caseSr=caseSr, model_idx=model_idx, fit_subset='test', idx_match_type='exact'
        )
        return self.predict_byModels(X=X, modelKeySr=modelKeySr, **kwargs)

    def predict_train(self, X: typeX, model_idx: int = 0, **kwargs: Any) -> np.ndarray:
        """ """
        assert isinstance(X, pd.DataFrame)
        assert self.caseField is not None
        assert self.caseField in X.columns
        caseSr: pd.Series = X[self.caseField]

        modelKeySr = self.get_modelKeySr(
            caseSr=caseSr, model_idx=model_idx, fit_subset='train', idx_match_type='exact'
        )
        return self.predict_byModels(X=X, modelKeySr=modelKeySr, **kwargs)

    def predict(self, X: typeX, skipCheck: bool = False, **kwargs: Any) -> np.ndarray:
        if not skipCheck:
            if isinstance(X, pd.DataFrame):
                if self.caseField is not None and self.caseField in X.columns:
                    trainCases = set(self._modelMapTrainCases[self.oosModelKey])
                    predCases = set(X[self.caseField].unique())
                    intersectCases = trainCases & predCases
                    assert not intersectCases, (
                        f'There are cases that are in predict and in train.: {intersectCases}'
                    )

        return self.predict_oos(X=X, **kwargs)

    def inverse_transform_pseudoOos(self, raw_pred_sr: pd.Series, caseSr: pd.Series) -> pd.Series:
        assert isinstance(raw_pred_sr, pd.Series)
        assert isinstance(caseSr, pd.Series)

        model_key_sr = self.get_modelKeySr(caseSr=caseSr, model_idx=0)

        score_sr_list = []
        gr = raw_pred_sr.groupby(model_key_sr)
        for model_key, tsr in gr:
            assert isinstance(model_key, str)
            sub_model = self.get_subModel(key=model_key)
            assert isinstance(sub_model, LeafModel)
            _score_sr = pd.Series(
                sub_model.outputTransformer.inverse_transform(tsr), index=tsr.index
            )
            score_sr_list.append(_score_sr)
        score_sr = pd.concat(score_sr_list, axis=0).reindex(raw_pred_sr.index)

        assert score_sr.index.equals(raw_pred_sr.index)
        return score_sr

    @staticmethod
    def _get_case_model_df(case_model_map: dict[str, list[str]]) -> pd.DataFrame:
        tsr = pd.concat(
            {k: pd.Series(el) for k, el in case_model_map.items()}, names=['model', '_']
        )
        tsr.name = 'case'
        case_model_df: pd.DataFrame = (
            tsr.reset_index('model')[['case', 'model']]
            .sort_values(['case', 'model'])
            .reset_index(drop=True)
        )
        assert not case_model_df.duplicated().any()
        case_model_df['modelIdx'] = functions.seqNr(case_model_df['case'])
        return case_model_df

    @cached({})
    def _test_case_model_df(self) -> pd.DataFrame:
        return self._get_case_model_df(case_model_map=self._modelMapTestCases)

    @cached({})
    def _train_case_model_df(self) -> pd.DataFrame:
        return self._get_case_model_df(case_model_map=self._modelMapTrainCases)

    @cached({})
    def get_caseMapModelSr(
        self, fit_subset: str = 'test', model_idx: int = 0, idx_match_type: str = 'exact'
    ) -> pd.Series:
        if fit_subset == 'test':
            case_model_df = self._test_case_model_df()
        elif fit_subset == 'train':
            case_model_df = self._train_case_model_df()
        else:
            raise ValueError(f'fit_subset `{fit_subset}` is not valid.')

        if idx_match_type == 'exact':
            map_sr = (
                case_model_df.loc[case_model_df['modelIdx'].eq(model_idx)]
                .set_index('case')['model']
                .astype(str)
            )
        elif idx_match_type == 'priority':
            tdf = case_model_df.copy()
            tdf['_sort'] = (tdf['modelIdx'] - model_idx - 0.1).abs()
            map_sr = tdf.sort_values('_sort', ascending=True).drop_duplicates('date', keep='first')
        else:
            raise ValueError(f'idx_match_type `{idx_match_type}` is not valid.')

        assert isinstance(map_sr, pd.Series)
        assert map_sr.index.is_unique

        return map_sr

    def get_modelIdx_max(self) -> int:
        return self._test_case_model_df()['modelIdx'].max()

    def get_trainCases_forSubModel(self, modelKey: str) -> list[str]:
        return self._modelMapTrainCases[modelKey].copy()

    def get_testCases_forSubModel(self, modelKey: str) -> list[str]:
        return self._modelMapTestCases[modelKey].copy()

    @staticmethod
    def _fit_single_submodel(
        inputDf: pd.DataFrame,
        targetSr: pd.Series,
        caseField: str,
        trainCases: list,
        model: LeafModel,
        fitKwargs: dict[str, Any],
    ) -> LeafModel:
        assert isinstance(inputDf, pd.DataFrame)
        assert isinstance(targetSr, pd.Series)
        assert caseField in inputDf.columns
        assert inputDf.shape[0] == targetSr.shape[0]
        assert inputDf.index.equals(targetSr.index)

        ind = inputDf[caseField].isin(trainCases).values
        assert ind.any()
        _in_df = inputDf.loc[ind]  # type: ignore[index]
        _in_target = targetSr.loc[ind]  # type: ignore[index]

        model = model.copy()
        model.fit(_in_df, _in_target.values, **fitKwargs)

        return model
