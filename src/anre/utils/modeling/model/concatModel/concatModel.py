# mypy: disable-error-code="assignment,misc,type-var,union-attr"
from typing import Any

import numpy as np
import pandas as pd

from anre.utils.modeling.model.concatModel.info import Info
from anre.utils.modeling.model.iModel import IModel
from anre.utils.modeling.model.iPredictModel import typeX
from anre.utils.modeling.model.leafModel.iLeafModel import ILeafModel
from anre.utils.modeling.model.modelHub.modelHub import ModelHub
from anre.utils.modeling.transformer.iTransformer import ITransformer
from anre.utils.worker.worker import Worker


class ConcatModel(ModelHub, IModel):  # type: ignore[override]
    """Modelis, kuris gali apungti kelis modelius, rezultatus grazinant iename masyve su apjungtadimensija

    Ekivalentu: np.concatenate([model1.predict, model2.predict], axis=1)

    Is esmes, tai modelHub'as pritemtas iki daugimacio modelio

    """

    __version__ = '0.0.0.1'
    classId: str = Info.get_expectedClassId()
    InfoClass = Info

    @classmethod
    def new_buildFit_fromLeafModel(
        cls,
        model: ILeafModel,
        X: pd.DataFrame,
        Y: pd.DataFrame,
        name: str | None = None,
        worker: Worker | None = None,
        fitKwargs: dict | None = None,
        attrs: dict | None = None,
        dropTargetNa=False,
        inputTransformer: ITransformer | None = None,
        outputTransformer: ITransformer | None = None,
        skipValidation=False,
    ):
        worker = Worker.new_sequential(show_progress=False) if worker is None else worker
        fitKwargs = dict() if fitKwargs is None else fitKwargs
        attrs = dict() if attrs is None else attrs
        name = 'ConcatModel' if name is None else name

        assert isinstance(model, ILeafModel)
        assert isinstance(X, pd.DataFrame)
        assert isinstance(Y, pd.DataFrame)
        assert isinstance(worker, Worker)
        assert isinstance(fitKwargs, dict)

        assert len(Y.shape) == 2
        assert Y.shape[-1] > 1, (
            'Technically we can runwith 1, but the meaning is lost. What was the intentions?'
        )
        assert not model.isFitted

        kwargsList = []
        for field, y in Y.items():
            _kwargs = {
                'modelBase': model,
                'X': X,
                'y': y,
                'fitKwargs': fitKwargs,
                'subModelName': f'{field}',
                'dropTargetNa': dropTargetNa,
            }
            kwargsList.append(_kwargs)

        models = worker.starmap(cls._buildFit_subModel_fromLeafModel, kwargs_list=kwargsList)

        return cls.new_fromList(
            models=models,
            name=name,
            attrs=attrs,
            useNamesAsKeys=True,
            inputTransformer=inputTransformer,
            outputTransformer=outputTransformer,
            skipValidation=skipValidation,
        )

    def __init__(
        self,
        modelDict: dict[str, IModel | str],
        name: str,
        attrs: dict,
        subModelKeys: list[str],
        isLazy: bool,
        inputTransformer: ITransformer | None = None,
        outputTransformer: ITransformer | None = None,
        skipValidation: bool = False,
    ):
        # we do not validate now, we validate at the end, so skipValidation=True
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

        self.isFitted = True
        self.output_shape = self._calc_outputShape(models=self.models)
        self.input_shape = (None, max([model.input_shape[1] for model in self._modelDict.values()]))
        self.isRegression = np.all([model.isRegression for model in self._modelDict.values()])
        self.isClassification = np.all([
            model.isClassification for model in self._modelDict.values()
        ])

        if not skipValidation:
            self.validate()

    def validate(self):
        super().validate()

        for key, model in self._modelDict.items():
            assert isinstance(model, IModel), (
                f'model(`{model}`) expected to be instance of IModel, but got {type(model)}'
            )
            assert model.isFitted
            input_shape = model.input_shape
            assert len(input_shape) == 2
            assert input_shape[0] is None
            assert input_shape[1] > 0

        assert self.output_shape == self._calc_outputShape(models=self._modelDict.values())

    @property
    def models(self) -> list[IModel]:
        return [self.get_subModel(key) for key in self.subModelKeys]

    def get_subModel(self, key: str) -> IModel:
        subModel = super().get_subModel(key=key)
        assert isinstance(subModel, IModel)
        return subModel

    def predict(self, X: typeX, **kwargs: Any) -> np.ndarray:
        X = self._inputTransformer.transform(X)
        resList = [model.predict(X=X, **kwargs) for model in self.models]

        # check dimensions and convert into 2D
        rowCount = resList[0].shape[0]
        fixedList = []
        for res in resList:
            assert res.shape[0] == rowCount
            if len(res.shape) == 1:
                res = res.reshape(-1, 1)
            assert len(res.shape) == 2
            fixedList.append(res)

        outputAr = np.hstack(fixedList)
        return self._outputTransformer.inverse_transform(outputAr)

    def get_predictDf(self, X: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        assert isinstance(X, pd.DataFrame)
        _pred = self.predict(X=X, **kwargs)
        predictDf = pd.DataFrame(_pred, index=X.index, columns=list(self.subModelKeys))
        return predictDf

    @staticmethod
    def _calc_outputShape(models: list[IModel]):
        outputDim = 0
        for model in models:
            assert isinstance(model, IModel), (
                f'model(`{model}`) expected to be instance of IModel, but got {type(model)}'
            )
            output_shape = model.output_shape
            if len(output_shape) == 1:
                _outputDim = 1
            elif len(output_shape) == 2:
                _outputDim = output_shape[1]
            else:
                raise NotImplementedError
            outputDim += _outputDim
        return None, outputDim

    @classmethod
    def _buildFit_subModel_fromLeafModel(
        cls, modelBase: ILeafModel, X, y, fitKwargs, subModelName, dropTargetNa
    ):
        model = modelBase.copy()
        if dropTargetNa:
            ind = ~np.isnan(y)
            if not ind.all():
                X = cls._dropNa(ind=ind, Xy=X)
                y = cls._dropNa(ind=ind, Xy=y)
        model.fit(X=X, y=y, **fitKwargs)
        model.set_name(name=subModelName)  # type: ignore[attr-defined]
        return model

    @staticmethod
    def _dropNa(ind: np.ndarray, Xy: pd.Series | pd.DataFrame | np.ndarray):
        if isinstance(Xy, (pd.DataFrame, pd.Series)):
            return Xy.loc[ind]
        elif isinstance(Xy, np.ndarray):
            return Xy[ind]
        else:
            raise NotImplementedError
