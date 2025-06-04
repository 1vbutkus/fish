import time
import traceback
from functools import wraps
from typing import Any, Callable
from warnings import warn

import numpy as np

from anre.utils.safeWrap.failedObj import FailedObj
from anre.utils.safeWrap.safeWrapResult import SafeWrapResult
from anre.utils.worker.iWorker import IWorker


class _NoDefault:
    pass


returnSafeWrapResult = _NoDefault()


class SafeWrap:
    @staticmethod
    def decorator(
        fun=None, *, verbose: bool = True, default=returnSafeWrapResult, raiseIfFailed=False
    ) -> Callable:
        assert fun is None, 'Please use SafeWrap.decorator() instead of @PersistentWrap.decorator'

        def _decorator(fun: Callable):
            @wraps(fun)
            def funWrapper(*args: Any, **kwargs: Any):
                startTime = time.time()
                try:
                    result = fun(*args, **kwargs)
                    finishTime = time.time()
                    saveWrapResult = SafeWrapResult(
                        success=True,
                        result=result,
                        takesTimeSec=finishTime - startTime,
                        errorStr='',
                        tracebackStr='',
                    )

                except BaseException as e:
                    finishTime = time.time()
                    saveWrapResult = SafeWrapResult(
                        success=False,
                        result=e,
                        takesTimeSec=finishTime - startTime,
                        errorStr=str(e),
                        tracebackStr=str(traceback.format_exc()),
                    )
                    if verbose:
                        msg = f'Failed to run function `{fun}`.Error: {e}.'
                        warn(msg)

                    if raiseIfFailed:
                        raise

                if isinstance(default, _NoDefault):
                    return saveWrapResult

                else:
                    if saveWrapResult.success:
                        return saveWrapResult.result

                    else:
                        return default

            return funWrapper

        return _decorator

    @classmethod
    def safeStarmap(
        cls,
        fun: Callable,
        argsTupleList: list | None = None,
        kwargsList: list | None = None,
        worker: IWorker | None = None,
        verbose: bool = True,
        **constKwargs,
    ) -> list[SafeWrapResult]:
        assert worker is not None, 'Please provide Worker'
        countArgs = len(argsTupleList) if argsTupleList else 0
        countKwargs = len(kwargsList) if kwargsList else 0
        countExpOutput = max(countArgs, countKwargs)

        resultSrFunWrapped = cls.decorator(verbose=False)(fun)
        wrappedResultList = worker.starmap(
            resultSrFunWrapped, args_tuple_list=argsTupleList, kwargs_list=kwargsList, **constKwargs
        )
        assert len(wrappedResultList) == countExpOutput
        successList = [wrappedResult.success for wrappedResult in wrappedResultList]
        if not all(successList) and verbose:
            wrappedResultList_bad = [
                wrappedResult for wrappedResult in wrappedResultList if not wrappedResult.success
            ]
            countBadCases = len(wrappedResultList_bad)
            wrappedResult = wrappedResultList_bad[0]
            msg = f'The are {countBadCases} bad cases in safeStarmap. Reporting on first error: {wrappedResult.errorStr}\ntraceback: {wrappedResult.tracebackStr}'
            warn(msg)

        return wrappedResultList

    @staticmethod
    def get_successResults(wrappedResultList: list[SafeWrapResult]) -> list[Any]:
        return [
            wrappedResult.result for wrappedResult in wrappedResultList if wrappedResult.success
        ]

    @staticmethod
    def get_resultsList(
        wrappedResultList: list[SafeWrapResult], objIfFailed=FailedObj(), verbose: bool = True
    ) -> list[Any]:
        badSuccess = [not wrappedResult.success for wrappedResult in wrappedResultList]
        if any(badSuccess) and verbose:
            (positions,) = np.where(badSuccess)
            wrappedResult = wrappedResultList[positions[0]]
            msg = f'The are {sum(badSuccess)} bad cases. In the positions: {list(positions)}. The first problem trase back: {wrappedResult.tracebackStr}'
            warn(msg)

        return [
            (wrappedResult.result if wrappedResult.success else objIfFailed)
            for wrappedResult in wrappedResultList
        ]
