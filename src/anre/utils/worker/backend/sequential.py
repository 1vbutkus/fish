import warnings
from typing import Any, Callable

from tqdm.auto import tqdm

from anre.utils.worker.backend.iBackend import IBackend


class Sequential(IBackend):
    def __init__(self, progress_desc: str | None = None) -> None:
        self._progress_desc = progress_desc

    def run(
        self,
        fun_list: list[Callable],
        args_tuple_list: list,
        kwargs_list: list,
        show_progress: bool,
        returnIfInterrupted: bool = False,
    ) -> list[Any]:
        iterator = zip(fun_list, args_tuple_list, kwargs_list)
        pbar = tqdm(
            total=len(kwargs_list),
            position=0,
            leave=True,
            disable=not show_progress,
            desc=self._progress_desc,
        )

        res_list = []
        try:
            for fun, args, kwargs in iterator:
                _res = fun(*args, **kwargs)
                res_list.append(_res)
                pbar.update(1)

        except KeyboardInterrupt:
            if returnIfInterrupted:
                msg = "The process Interrupted. Returning results up to that point."
                warnings.warn(msg)
            else:
                raise
        except BaseException:
            raise
        pbar.close()

        return res_list
