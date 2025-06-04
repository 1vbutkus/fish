# mypy: disable-error-code="assignment,var-annotated"
import time
from typing import Any, Callable

import pandas as pd


class FunctionsRunLog:
    """Funkciju paleidinijimo trakeris - kiek kartu, kik uztruko"""

    def __init__(self) -> None:
        self._takesTimeStepsInIteration = {}
        self._inCurrent = None
        self._startTime_step = 0

    def runFunction(self, fun: Callable, runLabel: str, *args: Any, **kwargs: Any):
        self._inCurrent = runLabel
        self._startTime_step = startTime = time.time()
        res = fun(*args, **kwargs)
        stopTime = time.time()
        runTime = stopTime - startTime
        self._inCurrent = None

        rec = self._takesTimeStepsInIteration.get(
            runLabel, {'label': runLabel, 'count': 0, 'lastTime': runTime, 'meanTime': runTime}
        )
        rec['count'] += 1
        rec['lastTime'] = runTime
        rec['meanTime'] = 0.1 * runTime + 0.9 * rec['meanTime']
        self._takesTimeStepsInIteration[runLabel] = rec
        self._inCurrent = None
        return res

    def get_reportDict(self) -> dict[str, dict]:
        return self._takesTimeStepsInIteration.copy()

    def get_reportDf(self) -> pd.DataFrame:
        reportDict = self.get_reportDict()
        df = pd.DataFrame(list(reportDict.values()))
        df.set_index('label', inplace=True)
        df.sort_index(inplace=True)
        return df

    def get_currentRun(self) -> tuple[float, str | None]:
        """Grazina runLable jei siuo metu runinama atitinkama funkcija"""
        if self._inCurrent is None:
            return 0.0, None
        else:
            runTime = time.time() - self._startTime_step
            return round(runTime, 2), self._inCurrent
