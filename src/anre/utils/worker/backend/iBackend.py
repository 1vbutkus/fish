import abc
from typing import Any, Callable


class IBackend(abc.ABC):
    @abc.abstractmethod
    def run(
        self,
        fun_list: list[Callable],
        args_tuple_list: list,
        kwargs_list: list,
        show_progress: bool,
    ) -> list[Any]: ...
