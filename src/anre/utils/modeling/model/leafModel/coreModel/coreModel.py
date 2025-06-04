# mypy: disable-error-code="assignment"
import os
from typing import Any

from anre.utils.modeling.model.leafModel.coreModel.coreModels.lgbmClassificationBinary import (
    LgbmClassificationBinary,
)
from anre.utils.modeling.model.leafModel.coreModel.coreModels.lgbmRegression import LgbmRegression
from anre.utils.modeling.model.leafModel.coreModel.coreModels.sklearnGeneral import SklearnGeneral
from anre.utils.modeling.model.leafModel.coreModel.iCoreModel import ICoreModel
from anre.utils.modeling.model.leafModel.coreModel.info import Info


class CoreModel:
    @classmethod
    def new_fromModelClassId(cls, classId: str, **params) -> 'ICoreModel':
        assert isinstance(params, dict)

        if classId == LgbmRegression.classId:
            coreModel = LgbmRegression.new(**params)

        elif classId == LgbmClassificationBinary.classId:
            coreModel = LgbmClassificationBinary.new(**params)

        elif classId == SklearnGeneral.classId:
            coreModel = SklearnGeneral.new(**params)

        else:
            from anre.utils.modeling.model.leafModel.coreModel.coreModels.kerasClassificationBinary import (
                KerasClassificationBinary,
            )
            from anre.utils.modeling.model.leafModel.coreModel.coreModels.kerasRegression import (
                KerasRegression,
            )

            if classId == KerasRegression.classId:
                coreModel = KerasRegression.new(**params)
            elif classId == KerasClassificationBinary.classId:
                coreModel = KerasClassificationBinary.new(**params)
            else:
                msg = f'classId(`{classId}`) is not Implemented in new_fromClassId.'
                raise NotImplementedError(msg)

        return coreModel

    @classmethod
    def new_fromEngine(cls, engine: Any, **kwargs: Any) -> 'ICoreModel':
        """Sita funkcijayra pagalbine,jei jau turi engine, tai gali bandyti sumapinti su CoreModel,bet nebutinai gaunasi"""

        if LgbmRegression.isValidEngine(engine=engine):
            coreModel = LgbmRegression.new_fromEngine(engine=engine, **kwargs)

        elif LgbmClassificationBinary.isValidEngine(engine=engine):
            coreModel = LgbmClassificationBinary.new_fromEngine(engine=engine, **kwargs)

        elif SklearnGeneral.isValidEngine(engine=engine):
            coreModel = SklearnGeneral.new_fromEngine(engine=engine, **kwargs)

        else:
            raise NotImplementedError
        return coreModel

    @classmethod
    def load(cls, dirPath: str) -> 'ICoreModel':
        assert os.path.exists(dirPath)
        assert os.path.isdir(dirPath)

        info = Info.load(dirPath=dirPath)

        if info.classId == LgbmRegression.classId:
            coreModel = LgbmRegression.load(dirPath=dirPath)
        elif info.classId == LgbmClassificationBinary.classId:
            coreModel = LgbmClassificationBinary.load(dirPath=dirPath)
        elif info.classId == SklearnGeneral.classId:
            coreModel = SklearnGeneral.load(dirPath=dirPath)
        else:
            from anre.utils.modeling.model.leafModel.coreModel.coreModels.kerasClassificationBinary import (
                KerasClassificationBinary,
            )
            from anre.utils.modeling.model.leafModel.coreModel.coreModels.kerasRegression import (
                KerasRegression,
            )

            if info.classId == KerasRegression.classId:
                coreModel = KerasRegression.load(dirPath=dirPath)
            elif info.classId == KerasClassificationBinary.classId:
                coreModel = KerasClassificationBinary.load(dirPath=dirPath)
            else:
                msg = f'classId {info.classId} is not Implemented in load function.'
                raise NotImplementedError(msg)

        return coreModel
