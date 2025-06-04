# mypy: disable-error-code="assignment"
from __future__ import annotations

from typing import Any, Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Colormap

from anre.utils.modeling.timeSlice.levelSlicer import LevelSlicer
from anre.utils.modeling.timeSlice.pureSlice import PureSlice


class TimeSlice:
    def __init__(self, pureSlice: PureSlice, generalTrainIds=None, parent=None) -> None:
        assert parent is None or isinstance(parent, TimeSlice)
        assert isinstance(pureSlice, PureSlice)
        generalTrainIds = pureSlice.get_trainIds() if generalTrainIds is None else generalTrainIds

        assert set(pureSlice.get_trainIds()) <= set(generalTrainIds)

        self.pureSlice = pureSlice
        self.generalTrainIds = generalTrainIds
        self.parent = parent
        self.childrenList: list[TimeSlice] | None = None

        assert set(self.generalTrainIds) >= set(self.get_trainIds())
        assert not set(self.generalTrainIds) & set(self.get_testIds())

    def __repr__(self) -> str:
        trainRepr = self._list_repr(self.get_trainIds())
        testRepr = self._list_repr(self.get_testIds())
        hierarchyIdList = self._get_hierarchyIdList()
        idsRepr = ','.join([str(el) for el in hierarchyIdList]) if hierarchyIdList else 'root'

        childsRepr = ''
        if self.childrenList:
            hierarchyLevel = self._get_hierarchyLevel()
            childsRepr = '\n' + '\n'.join([
                '    ' * (hierarchyLevel) + f' - {child.__repr__()}' for child in self.childrenList
            ])

        msg = f'timeSlice({idsRepr}): {trainRepr} -> {testRepr}{childsRepr}'
        return msg

    def get_testIds(self) -> list[int]:
        return self.pureSlice.get_testIds()

    def get_trainIds(self) -> list[int]:
        return self.pureSlice.get_trainIds()

    def get_generalTrainIds(self) -> list[int]:
        return self.generalTrainIds

    def get_relatedIds(self) -> set:
        return set(self.generalTrainIds).union(set(self.get_testIds()))

    def get_trainValues(self) -> list:
        return self.pureSlice.get_trainValues()

    def get_testValues(self) -> list:
        return self.pureSlice.get_testValues()

    def get_values(self) -> list:
        return self.pureSlice.get_values()

    def get_sliceId(self) -> int | None:
        return self.pureSlice.get_sliceId()

    def get_allIds(self) -> list[int]:
        allIds = self.pureSlice.get_allIds()
        return allIds

    def get_childrenList(self) -> list[TimeSlice]:
        return [] if self.childrenList is None else self.childrenList

    def add_children(self, levelSlicerList: list[LevelSlicer]) -> None:
        assert self.childrenList is None

        levelSlicer = levelSlicerList[0]
        splitIdsGenerator = levelSlicer.get_splitIdsGenerator(
            parentGeneralTrainIds=self.generalTrainIds
        )
        childrenList = []
        # splitIdsDict = next(splitIdsDictGenerator)
        for splitIds in splitIdsGenerator:
            pureSlice = PureSlice(
                sliceId=splitIds.sliceId,
                values=self.get_values(),
                trainIds=splitIds.trainIds,
                testIds=splitIds.testIds,
            )
            timeSlice_level_i = TimeSlice(
                pureSlice=pureSlice,
                generalTrainIds=splitIds.generalTrainIds,
                parent=self,
            )
            if len(levelSlicerList) > 1:
                timeSlice_level_i.add_children(levelSlicerList[1:])
            childrenList.append(timeSlice_level_i)

        self.childrenList = childrenList

    def plot(
        self,
        maxLevel=-1,
        aspect: Literal["equal", "auto"] | float | None = "auto",
        cmap: str | Colormap | None = None,
        **kwargs: Any,
    ):
        if cmap is None:
            cmap = plt.colormaps.get_cmap('Blues')

        timeSliceList = self._treeToList(maxLevel=maxLevel)
        allIds = self.get_allIds()
        hierarchyLevelMax = max([timeSlice._get_hierarchyLevel() for timeSlice in timeSliceList])

        shape = len(timeSliceList), len(allIds)
        mat = np.zeros(shape)
        for sliceId, timeSlice in enumerate(timeSliceList):
            hierarchyLevel = timeSlice._get_hierarchyLevel()
            if hierarchyLevel > 0:
                mat[sliceId, timeSlice.get_trainIds()] = (
                    1 + (hierarchyLevelMax - hierarchyLevel) * 2
                )
                mat[sliceId, timeSlice.get_testIds()] = 2 + (hierarchyLevelMax - hierarchyLevel) * 2

        return plt.imshow(mat, interpolation='nearest', cmap=cmap, aspect=aspect, **kwargs)

    def _get_hierarchyIdList(self) -> list[int]:
        if self.parent is None:
            hierarchyIdList = [self.get_sliceId()]
            return [el for el in hierarchyIdList if el is not None]
        elif isinstance(self.parent, self.__class__):
            hierarchyIdList = self.parent._get_hierarchyIdList()
            hierarchyIdList.append(self.get_sliceId())
            return hierarchyIdList  # type: ignore[return-value]
        else:
            raise ValueError

    def _get_hierarchyLevel(self) -> int:
        hierarchyIdList = self._get_hierarchyIdList()
        return len(hierarchyIdList)

    def _treeToList(self, maxLevel=-1) -> list[TimeSlice]:
        timeSliceList = []

        def _collectAll(timeSlice: TimeSlice):
            if maxLevel >= 0:
                levelRemaining = maxLevel - timeSlice._get_hierarchyLevel()
            else:
                levelRemaining = 1
            if levelRemaining >= 0:
                timeSliceList.append(timeSlice)
            if levelRemaining > 0 and timeSlice.childrenList:
                for children in timeSlice.childrenList:
                    _collectAll(children)

        _collectAll(timeSlice=self)
        return timeSliceList

    @staticmethod
    def _list_repr(listItem):
        if len(listItem) == 0:
            return '(#0) None'
        else:
            sr = pd.Series(listItem)
            skipInd = (sr.shift(1).add(1) == sr) & (sr.shift(-1).add(-1) == sr)
            blankInd = skipInd & skipInd.shift(1)
            srStr = sr.astype(str)
            srStr[skipInd] = '..'
            srStr[blankInd] = None
            srStr.dropna(inplace=True)
            elemsStr = ','.join(srStr)
            return f'(#{len(listItem)})[{elemsStr}]'
