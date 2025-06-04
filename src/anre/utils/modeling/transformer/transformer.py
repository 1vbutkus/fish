# mypy: disable-error-code="assignment"
import os
from typing import Any

from anre.utils.modeling.transformer.info import Info
from anre.utils.modeling.transformer.iTransformer import ITransformer
from anre.utils.modeling.transformer.transformers.ecdf import Ecdf
from anre.utils.modeling.transformer.transformers.identity import Identity
from anre.utils.modeling.transformer.transformers.sklearnGeneral import SklearnGeneral


class Transformer:
    @classmethod
    def new_fromClassId(cls, classId: str, **kwargs: Any) -> 'ITransformer':
        if classId == Identity.classId:
            scaler = Identity.new(**kwargs)

        elif classId == SklearnGeneral.classId:
            scaler = SklearnGeneral.new(**kwargs)

        elif classId == Ecdf.classId:
            scaler = Ecdf.new(**kwargs)

        else:
            msg = f'classId {classId} is not Implemented in load new_fromClassId.'
            raise NotImplementedError(msg)

        return scaler

    @classmethod
    def new_identity(cls, **kwargs: Any) -> Identity:
        return Identity.new(**kwargs)

    @classmethod
    def new_sklearnGeneral(cls, **kwargs: Any) -> SklearnGeneral:
        return SklearnGeneral.new(**kwargs)

    @classmethod
    def new_sklearn_scale(cls, **kwargs: Any) -> SklearnGeneral:
        return SklearnGeneral.new_scaler(**kwargs)

    @classmethod
    def new_sklearn_scalePca(cls, **kwargs: Any) -> SklearnGeneral:
        return SklearnGeneral.new_scalePca(**kwargs)

    @classmethod
    def load(cls, dirPath: str) -> 'ITransformer':
        assert os.path.exists(dirPath)
        assert os.path.isdir(dirPath)

        info = Info.load(dirPath=dirPath)

        if info.classId == Identity.classId:
            scaler = Identity.load(dirPath=dirPath)
        elif info.classId == SklearnGeneral.classId:
            scaler = SklearnGeneral.load(dirPath=dirPath)
        elif info.classId == Ecdf.classId:
            scaler = Ecdf.load(dirPath=dirPath)
        else:
            msg = f'classId {info.classId} is not Implemented in load function.'
            raise NotImplementedError(msg)

        return scaler
