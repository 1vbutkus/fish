from typing import Any

from sklearn.base import is_classifier as _is_classifier
from sklearn.base import is_regressor as _is_regressor
from sklearn.pipeline import Pipeline


def isFromSklearn(obj: Any) -> bool:
    """This is hack and guess, should not hevelly rely on"""
    return "'sklearn." in str(type(obj))


def isSklearnModel(model: Any) -> bool:
    return isFromSklearn(model) and (_is_regressor(model) or _is_classifier(model))


def get_lastStep_fromPipeline(pipe: Pipeline) -> Any:
    assert isinstance(pipe, Pipeline)
    lastStep = pipe.steps[-1][1]
    return lastStep


def extract_model(modelOrPipe: Any) -> Any:
    if isinstance(modelOrPipe, Pipeline):
        model = get_lastStep_fromPipeline(pipe=modelOrPipe)
    else:
        model = modelOrPipe
    assert isSklearnModel(model)
    return model


def isRegressor(model: Any) -> bool:
    return _is_regressor(model)


def isClassifier(model: Any) -> bool:
    return _is_classifier(model)
