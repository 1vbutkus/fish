import abc

import numpy as np
import pandas as pd

from anre.utils.modeling.model.leafModel.coreModel.iCoreModel import ICoreModel

typeX = pd.DataFrame | np.ndarray


class ILeafModel(ICoreModel):
    xFields: list[str]
    coreModel: ICoreModel

    @abc.abstractmethod
    def predict(
        self, X: typeX, chunkSize: int | None = None, skipPredScale: bool = False, **kwargs
    ) -> np.ndarray: ...

    @abc.abstractmethod
    def set_name(self, name: str) -> None: ...
