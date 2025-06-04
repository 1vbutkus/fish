from typing import Any

from anre.utils.worker.worker import Worker


def double(x: int) -> int:
    return x * 2


def double_at_scale(x_list: list[int]) -> list[int]:
    kwargs_list = [{'x': x} for x in x_list]
    worker = Worker.new_multiproc(
        show_progress=True, max_worker=30, progress_desc='double_at_scale'
    )
    res_list = worker.starmap(
        fun=double,
        kwargs_list=kwargs_list,
    )
    return res_list


def double_in_nest(x_list_list: list[list[int]], allowedNest: bool) -> list[Any]:
    kwargs_list = [{'x_list': x_list} for x_list in x_list_list]
    worker = Worker.new_multiproc(
        show_progress=True, max_worker=30, allowedNest=allowedNest, progress_desc='double_in_nest'
    )
    res_list = worker.starmap(
        fun=double_at_scale,
        kwargs_list=kwargs_list,
    )
    return res_list
