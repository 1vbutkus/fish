from typing import Any

from anre.utils.modeling.model.hyperParameters.backend.iBackend import IBackend
from anre.utils.modeling.model.hyperParameters.hyperParameter import HyperParameter


class Lgbm(IBackend):
    # cia ne visi parametrai, tik tie kurie pasirode idomus
    _parameterList: list[HyperParameter] = [
        HyperParameter(
            label="boosting_type",
            type="str",
            value="gbdt",
            admissibleValues=("gbdt", "dart", "goss", "rf"),
        ),
        HyperParameter(
            label="num_leaves",
            type="int",
            value=31,
            softLims=(10, 256),
            hardLims=(2, 131072),
            comment="This is the main parameter to control the complexity of the tree strategy.",
        ),
        HyperParameter(
            label="max_bin",
            type="int",
            value=255,
            softLims=(10, 1000),
            hardLims=(2, 1e9),
        ),
        HyperParameter(
            label="max_depth",
            type="int",
            value=-1,
            softLims=(-1, 1000000),
            hardLims=(-1, 1e9),
        ),
        HyperParameter(
            label="n_estimators",
            type="int",
            value=100,
            softLims=(10, 300),
            hardLims=(-1, 1e9),
        ),
        HyperParameter(
            label="learning_rate",
            type="float",
            value=0.1,
            softLims=(0, 0.5),
            hardLims=(0, 1),
        ),
        HyperParameter(
            label="min_split_gain",
            type="float",
            value=0.0,
            softLims=(0, 100),
            hardLims=(0, 1e9),
        ),
        HyperParameter(
            label="min_child_samples",
            type="int",
            value=20,
            softLims=(10, 1000000),
            hardLims=(0, 1e9),
        ),
        HyperParameter(
            label="reg_alpha",
            type="float",
            value=0.0,
            softLims=(0, 10),
            hardLims=(0, 1e9),
        ),
        HyperParameter(
            label="reg_lambda",
            type="float",
            value=0.0,
            softLims=(0, 10),
            hardLims=(0, 1e9),
        ),
    ]

    @classmethod
    def get_hyperParameterList(cls, **kwargs: Any) -> list[HyperParameter]:
        return cls._parameterList.copy()
