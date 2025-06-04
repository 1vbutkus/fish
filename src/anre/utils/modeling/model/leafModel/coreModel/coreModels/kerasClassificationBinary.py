from typing import Any

from anre.utils.modeling.model.leafModel.coreModel.coreModels.kerasRegression import (
    KerasRegression,
    TfWrapper,
)

# FIXME: Add missing files with the below types
# from anre.utils.modeling.tensorflow_.wrapper.wrapper import Wrapper as TfWrapper


class KerasClassificationBinary(KerasRegression):
    classId: str = 'KerasClassificationBinary'
    isRegression: bool = False
    isClassification: bool = True

    @staticmethod
    def _engineFactory(**kwargs: Any) -> TfWrapper:
        """This one returns function that build ts object"""
        return TfWrapper.new_classificationBinary_robust(**kwargs)  # type: ignore[attr-defined]
