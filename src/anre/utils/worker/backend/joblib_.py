from typing import Any, Callable

import joblib

from anre.utils.worker.backend.iBackend import IBackend


class Joblib(IBackend):
    def __init__(self, maxWorker: int = -2, prefer: str | None = None) -> None:
        assert isinstance(maxWorker, int) and maxWorker > 0
        self._prefer = prefer or 'processes'
        self._maxWorker = maxWorker

    def run(
        self,
        fun_list: list[Callable],
        args_tuple_list: list,
        kwargs_list: list,
        show_progress: bool,
    ) -> list[Any]:
        xs = list(zip(fun_list, args_tuple_list, kwargs_list))
        _poolSize = min(len(xs), self._maxWorker)

        with joblib.Parallel(
            n_jobs=_poolSize,
            prefer=self._prefer,
            verbose=10 if show_progress else 0,
        ) as runner:
            resultList = runner(joblib.delayed(fun)(*args, **kwargs) for fun, args, kwargs in xs)
            runner._backend.abort_everything()

        return resultList
