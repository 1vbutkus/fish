from typing import Any

import numpy as np
from lightgbm import LGBMClassifier

from anre.utils.modeling.model.leafModel.coreModel.coreModels.lgbmRegression import LgbmRegression


class LgbmClassificationBinary(LgbmRegression):
    classId: str = 'LgbmClassificationBinary'
    isRegression: bool = False
    isClassification: bool = True

    _engineClass = LGBMClassifier

    def predict(self, X, n_jobs=1, **kwargs: Any) -> np.ndarray:
        return self._engine.predict_proba(X, n_jobs=n_jobs, **kwargs)[:, 1]
