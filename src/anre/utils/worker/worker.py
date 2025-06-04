# mypy: disable-error-code="assignment,operator"
from __future__ import annotations

from itertools import repeat
from os import cpu_count
from typing import Any, Callable, Iterable

from more_itertools import take

from anre.utils.worker.backend.iBackend import IBackend
from anre.utils.worker.backend.joblib_ import Joblib
from anre.utils.worker.backend.multiProc import MultiProc
from anre.utils.worker.backend.sequential import Sequential
from anre.utils.worker.backend.thread import Thread
from anre.utils.worker.iWorker import IWorker


class Worker(IWorker):
    @classmethod
    def new(
        cls,
        label: str | None = None,
        show_progress: bool = False,
        max_worker: int | None = None,
        **kwargs,
    ) -> 'Worker':
        if label is None:
            if (max_worker is None) or (max_worker == 1):
                label = 'sequential'
            else:
                label = 'joblib'

        assert isinstance(label, str)
        if label == 'sequential':
            assert not kwargs
            assert (max_worker is None) or (max_worker == 1)
            return cls.new_sequential(show_progress=show_progress)

        elif label == 'thread':
            assert not kwargs
            return cls.new_thread(show_progress=show_progress, max_worker=max_worker)  # type: ignore[arg-type]

        elif label == 'multiproc':
            assert set(kwargs) <= {'startMethod'}
            return cls.new_multiproc(show_progress=show_progress, max_worker=max_worker, **kwargs)

        elif label == 'joblib':
            assert not kwargs
            return cls.new_joblib(show_progress=show_progress, max_worker=max_worker)

        else:
            raise NotImplementedError(f'label(`{label}`) is not supported in Worker.new')

    @classmethod
    def new_sequential(
        cls, show_progress: bool = False, progress_desc: str | None = None
    ) -> Worker:
        return cls(backend=Sequential(progress_desc=progress_desc), show_progress=show_progress)

    @classmethod
    def new_thread(cls, show_progress: bool = False, max_worker: int = 5) -> Worker:
        return cls(backend=Thread(maxWorker=max_worker), show_progress=show_progress)

    @classmethod
    def new_multiproc(
        cls,
        show_progress=False,
        max_worker: int | None = None,
        start_method: str = 'spawn',
        allowedNest: bool = False,
        progress_desc: str | None = None,
    ) -> Worker:
        max_worker = cls._get_max_worker_int(max_worker=max_worker)
        return cls(
            backend=MultiProc(
                maxWorker=max_worker,
                startMethod=start_method,
                allowedNest=allowedNest,
                progress_desc=progress_desc,
            ),
            show_progress=show_progress,
        )

    @classmethod
    def new_joblib(
        cls,
        show_progress: bool = False,
        max_worker: int | None = None,
        prefer: str | None = None,
    ) -> Worker:
        max_worker = cls._get_max_worker_int(max_worker=max_worker)
        return cls(backend=Joblib(maxWorker=max_worker, prefer=prefer), show_progress=show_progress)

    def __init__(self, backend: IBackend, show_progress: bool = False) -> None:
        self._showProgress = show_progress
        self._backend = backend

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}({self._backend.__class__.__name__}, show_progress={self._showProgress})>'

    def map(self, fun: Callable, *args: Any, **kwargs: Any) -> list[Any]:
        assert all([isinstance(arg, Iterable) for arg in args + tuple(kwargs.values())]), (
            'All worker arguments must be iteratible'
        )

        len_iterables = [arg for arg in args + tuple(kwargs.values()) if hasattr(arg, '__len__')]
        assert len_iterables, 'At least one argument must be finite size'

        argCount = len(len_iterables[0])
        assert all(len(arg) == argCount for arg in len_iterables), (
            'Worker arguments must have the same length'
        )

        args = [take(argCount, x) for x in args]
        kwargs = {k: take(argCount, v) for k, v in kwargs.items()}

        args_tuple_list = list(zip(*args))
        kwargs_list = (
            [{k: kwargs[k][i] for k in kwargs.keys()} for i in range(argCount)]
            if len(kwargs) > 0
            else []
        )

        return self.starmap(fun=fun, args_tuple_list=args_tuple_list, kwargs_list=kwargs_list)

    def starmap(
        self,
        fun: Callable,
        args_tuple_list: list | None = None,
        kwargs_list: list | None = None,
        **const_kwargs,
    ) -> list[Any]:
        args_tuple_list = args_tuple_list if args_tuple_list else []
        kwargs_list = kwargs_list if kwargs_list else []
        assert args_tuple_list or kwargs_list, 'No parameters to map(in worker)'

        args_tuple_list = args_tuple_list if len(args_tuple_list) > 0 else [()] * len(kwargs_list)
        kwargs_list = kwargs_list if len(kwargs_list) > 0 else [{}] * len(args_tuple_list)
        assert len(args_tuple_list) == len(kwargs_list)

        args_tuple_list = (
            args_tuple_list
            if type(args_tuple_list[0]) is tuple
            else [(argsTuple,) for argsTuple in args_tuple_list]
        )

        fun_list = [fun] * len(args_tuple_list)

        return self.run(
            fun_list=fun_list,
            args_tuple_list=args_tuple_list,
            kwargs_list=kwargs_list,
            **const_kwargs,
        )

    def run(
        self,
        fun_list: list[Callable],
        args_tuple_list: list | None = None,
        kwargs_list: list | None = None,
        **const_kwargs,
    ) -> list[Any]:
        args_tuple_list = args_tuple_list if args_tuple_list else []
        kwargs_list = kwargs_list if kwargs_list else []
        assert fun_list

        args_tuple_list = args_tuple_list if len(args_tuple_list) > 0 else [()] * len(fun_list)
        kwargs_list = kwargs_list if len(kwargs_list) > 0 else [{}] * len(fun_list)
        assert len(args_tuple_list) == len(kwargs_list) == len(fun_list)

        if const_kwargs:
            keySet = set(const_kwargs)
            newKwargsList = []
            for kwargs in kwargs_list:
                assert not (overKwargs := set(kwargs) & keySet), (
                    f'Const overrider kwargsList: {overKwargs}'
                )
                kwargs = kwargs.copy()
                kwargs.update(const_kwargs)
                newKwargsList.append(kwargs)
            kwargs_list = newKwargsList

        return self._backend.run(
            fun_list=fun_list,
            args_tuple_list=args_tuple_list,
            kwargs_list=kwargs_list,
            show_progress=self._showProgress,
        )

    @staticmethod
    def const(x):
        return repeat(x)

    @staticmethod
    def _get_max_worker_int(max_worker: int | None) -> int:
        assert max_worker is None or isinstance(max_worker, int)
        max_worker = max_worker if max_worker else -2  # this is due to historical compatability
        if max_worker < 0:
            max_worker = max(1, int(cpu_count() + 1 + max_worker))
        assert isinstance(max_worker, int) and max_worker > 0
        return max_worker
