# mypy: disable-error-code="attr-defined"
import pandas as pd

from anre.utils.indicator.ema.emaSingle import EmaSingle


class Ema:
    def __init__(self, halflifes: list[float | int], adjust: bool = True) -> None:
        assert isinstance(halflifes, list)
        assert isinstance(adjust, bool)
        assert halflifes

        self._emaSingleList = [
            EmaSingle(halflife=halflife, adjust=adjust) for halflife in halflifes
        ]

    def update(self, sr: pd.Series):
        for emaSingle in self._emaSingleList:
            emaSingle.update(sr=sr)

    def get_currentState(self) -> pd.Series:
        return pd.concat([
            emaSingle.get_currentState(rename=True) for emaSingle in self._emaSingleList
        ])

    def updateReturn(self, sr: pd.Series) -> pd.Series:
        self.update(sr=sr)
        return self.get_currentState()
