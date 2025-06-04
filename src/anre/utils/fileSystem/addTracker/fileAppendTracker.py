# mypy: disable-error-code="assignment"
import os
import warnings
from collections import Counter, deque
from threading import Lock

from anre.utils import functions


class FileAppendTracker:
    def __init__(self, filePath: str) -> None:
        assert isinstance(filePath, str)

        if not os.path.exists(filePath):
            warnings.warn(f'File is missing: {filePath}')

        self._filePath: str = filePath
        self._lastRowCount: int = 0
        self._lastStat = None
        self._countLogLevels = ['WARNING', 'ERROR', 'CRITICAL']
        self._logLevelCounter = Counter({level: 0 for level in self._countLogLevels})
        self._lock = Lock()
        self._linesDeque: deque[str] = deque()

    def get_newLines(self) -> list[str]:
        self._update_newLines()
        return list(functions.yield_popleft(self._linesDeque))

    def get_logLevelCounts(self) -> dict:
        self._update_newLines()
        return dict(self._logLevelCounter)

    def get_lastRowCount(self) -> int:
        self._update_newLines()
        return self._lastRowCount

    #####################################################################

    def _update_newLines(self) -> None:
        with self._lock:
            newLines = []
            if os.path.exists(self._filePath):
                stat = os.stat(self._filePath)
                if self._lastStat is None:
                    self._lastStat = stat
                    isChange = True
                else:
                    isChange = (self._lastStat.st_size != stat.st_size) or (
                        self._lastStat.st_atime != stat.st_atime
                    )
                    self._lastStat = stat

                if isChange:
                    with open(self._filePath, "r") as f:
                        lines = f.readlines()

                    newLines = lines[self._lastRowCount :]
                    self._lastRowCount = len(lines)

            else:
                self._lastStat = None
                self._lastRowCount = 0
                warnings.warn(f'File is missing: {self._filePath}')

            # update loglevel counter
            for line in newLines:
                for level in self._countLogLevels:
                    if level in line:
                        self._logLevelCounter.update([level])

            if newLines:
                self._linesDeque.extend(newLines)


def __demo__() -> None:
    filePath = '/mnt/D/bird/procData/strategyRun/33141278/logs/warnings.log'
    fileAppendTracker = FileAppendTracker(filePath=filePath)

    fileAppendTracker.get_newLines()
