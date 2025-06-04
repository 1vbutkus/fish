# mypy: disable-error-code="assignment,misc"
import multiprocessing
import multiprocessing.pool
from typing import Any, Callable

from tqdm.auto import tqdm

from anre.utils.worker.backend.iBackend import IBackend


class NoDaemonProcess(multiprocessing.Process):
    @property
    def daemon(self):
        return False

    @daemon.setter
    def daemon(self, value: bool) -> None:
        pass


class MultiProc(IBackend):
    def __init__(
        self,
        startMethod: str,
        maxWorker: int = -2,
        allowedNest: bool = False,
        progress_desc: str | None = None,
    ):
        assert isinstance(maxWorker, int) and maxWorker > 0
        self._maxWorker = maxWorker
        assert startMethod in (x := ['fork', 'spawn', 'forkserver']), (
            f'Only these process start method are allowed: {x}'
        )
        self._startMethod = startMethod
        self._allowedNest = allowedNest
        self._progress_desc = progress_desc

    def run(
        self,
        fun_list: list[Callable],
        args_tuple_list: list,
        kwargs_list: list,
        show_progress: bool,
    ) -> list[Any]:
        xs = list(zip(range(len(fun_list)), fun_list, args_tuple_list, kwargs_list))
        _poolSize = min(len(xs), self._maxWorker)

        if self._allowedNest:

            class NoDaemonContext(type(multiprocessing.get_context(self._startMethod))):
                Process = NoDaemonProcess

            context = NoDaemonContext()
        else:
            context = multiprocessing.get_context(self._startMethod)

        if show_progress:
            pool_result_list = []
            with multiprocessing.pool.Pool(processes=_poolSize, context=context) as pool:
                with tqdm(total=len(xs), desc=self._progress_desc) as pbar:
                    for i, resEl in enumerate(pool.imap_unordered(self._lamda_helper, xs)):
                        pool_result_list.append(resEl)
                        pbar.update()

        else:
            with multiprocessing.pool.Pool(processes=_poolSize, context=context) as pool:
                pool_result_list = pool.map(self._lamda_helper, xs)

        pool_result_list.sort(key=lambda r: r[0])
        result_list = [el[1] for el in pool_result_list]

        return result_list

    @staticmethod
    def _lamda_helper(x) -> tuple[int, Any]:
        nr, f, args, kwargs = x
        return nr, f(*args, **kwargs)
