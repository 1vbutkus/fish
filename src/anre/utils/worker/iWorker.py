import abc
from typing import Any, Callable, TypeVar

T = TypeVar('T')


class IWorker(abc.ABC):
    @abc.abstractmethod
    def map(self, fun: Callable, *args: Any, **kwargs: Any) -> list[Any]: ...

    @abc.abstractmethod
    def starmap(
        self,
        fun: Callable,
        args_tuple_list: list | None = None,
        kwargs_list: list | None = None,
        **const_kwargs: Any,
    ) -> list[Any]: ...

    @abc.abstractmethod
    def run(
        self,
        fun_list: list[Callable],
        args_tuple_list: list | None = None,
        kwargs_list: list | None = None,
        **const_kwargs: Any,
    ) -> list[Any]: ...

    @staticmethod
    @abc.abstractmethod
    def const(x: T) -> T: ...
