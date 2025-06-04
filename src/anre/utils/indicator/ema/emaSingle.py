# mypy: disable-error-code="operator,union-attr"
import numpy as np
import pandas as pd


class EmaSingle:
    def __init__(self, halflife: float | int, adjust: bool = True) -> None:
        assert isinstance(halflife, (float, int))
        assert isinstance(adjust, bool)
        assert halflife > 0

        self._halflife = halflife
        self._1MinusAlpha = 1.0 - self.get_alpha(halflife=halflife)
        self._adjust = adjust
        self._currentState: pd.Series | None = None
        self._nomSum: pd.Series | float = 0.0
        self._deNomSum: np.ndarray | float = 0.0

    @staticmethod
    def get_alpha(halflife: float | int) -> float:
        assert halflife > 0
        return 1.0 - np.exp(-np.log(2) / halflife)

    def update(self, sr: pd.Series):
        if self._adjust:
            self._deNomSum = (~sr.isna()).values + self._1MinusAlpha * self._deNomSum
            self._nomSum = sr.fillna(0) + self._1MinusAlpha * self._nomSum
            self._currentState = self._nomSum / self._deNomSum

        else:
            if self._currentState is None:
                self._currentState = sr.copy()
            else:
                assert isinstance(self._currentState, pd.Series)
                assert len(self._currentState) == len(sr)
                assert self._currentState.index.equals(sr.index)
                self._currentState = (
                    self._1MinusAlpha * self._currentState + (1 - self._1MinusAlpha) * sr
                )

    def get_currentState(self, rename: bool = False) -> pd.Series:
        if rename:
            index = [f'{field}_ema{self._halflife}' for field in self._currentState.index]
            sr = self._currentState.copy()
            sr.index = index
            return sr
        else:
            assert self._currentState is not None
            return self._currentState

    def updateReturn(self, sr: pd.Series) -> pd.Series:
        self.update(sr=sr)
        assert self._currentState is not None
        return self._currentState
