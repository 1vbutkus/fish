from multiprocessing.pool import ThreadPool
from typing import Any, Callable

import tqdm

from anre.utils.worker.backend.iBackend import IBackend


class Thread(IBackend):
    def __init__(self, maxWorker: int = 5) -> None:
        assert isinstance(maxWorker, int) and maxWorker > 0
        self._maxWorker = maxWorker

    def run(
        self,
        fun_list: list[Callable],
        args_tuple_list: list,
        kwargs_list: list,
        show_progress: bool,
    ) -> list[Any]:
        xs = list(zip(range(len(fun_list)), fun_list, args_tuple_list, kwargs_list))
        _poolSize = min(len(xs), self._maxWorker)

        if show_progress:
            poolResultList = []
            with ThreadPool(_poolSize) as pool:
                with tqdm.tqdm(total=len(xs)) as pbar:
                    for i, resEl in enumerate(pool.imap_unordered(self._lamdaHelper, xs)):
                        poolResultList.append(resEl)
                        pbar.update()
        else:
            with ThreadPool(_poolSize) as pool:
                poolResultList = pool.map(self._lamdaHelper, xs)

        poolResultList.sort(key=lambda r: r[0])
        resultList = [el[1] for el in poolResultList]

        return resultList

    @staticmethod
    def _lamdaHelper(x) -> tuple[int, Any]:
        nr, f, args, kwargs = x
        return nr, f(*args, **kwargs)
