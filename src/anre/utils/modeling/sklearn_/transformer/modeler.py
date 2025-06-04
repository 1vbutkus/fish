import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class Modeler(TransformerMixin, BaseEstimator):
    def __init__(
        self, *, model, x_fields: list[str], y_fields: list[str], residuals: bool = True
    ) -> None:
        self.model = model
        self.x_fields = x_fields
        self.y_fields = y_fields
        self.residuals = residuals

    def fit(self, X, y=None):
        assert isinstance(X, pd.DataFrame)
        self.model.fit(X[self.x_fields], X[self.y_fields])
        return self

    def transform(self, X):
        assert isinstance(X, pd.DataFrame)
        if self.residuals:
            return X[self.y_fields] - self.model.predict(X[self.x_fields])
        else:
            return pd.DataFrame(
                self.model.predict(X[self.x_fields]), index=X.index, columns=self.y_fields
            )
