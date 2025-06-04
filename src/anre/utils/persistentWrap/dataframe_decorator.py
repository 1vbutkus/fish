import os
import tempfile
from typing import Callable, ParamSpec, Protocol, TypeVar, cast

import pandas as pd

from anre.utils.path_template import PathTemplate, PathTemplateArgType

ArgType = PathTemplateArgType
T = TypeVar('T')
P = ParamSpec('P')


class DataFrameDecoratedCallable(Protocol[P]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> pd.DataFrame: ...

    def ensure_path(self, *args: P.args, **kwargs: P.kwargs) -> str: ...


class DataFrameDecorator:
    def __init__(self, path_template: str, cache_path: str, skip_args: list[str] | None = None):
        assert os.path.isabs(cache_path)
        self._path_template = PathTemplate(path_template)
        self._cache_path = cache_path
        self._fun: Callable | None = None
        self._skip_args = skip_args or []

    def __call__(self, fun: Callable[P, pd.DataFrame]) -> DataFrameDecoratedCallable[P]:
        def wrapped_fun(**kwargs: ArgType) -> pd.DataFrame:
            file_path = self._get_file_path(kwargs)

            if os.path.exists(file_path):
                return pd.read_parquet(file_path)

            df = fun(**kwargs)  # type: ignore[arg-type,call-arg]
            self._save_to_parquet(df, file_path)
            return df

        self._fun = fun
        wrapped_fun.wrapper = self  # type: ignore[attr-defined]
        wrapped_fun.ensure_path = self.ensure_path  # type: ignore[attr-defined]

        return cast(DataFrameDecoratedCallable, wrapped_fun)

    def ensure_path(self, **kwargs: ArgType) -> str:
        assert self._fun is not None

        file_path = self._get_file_path(kwargs)

        if os.path.exists(file_path):
            return file_path

        df = self._fun(**kwargs)
        self._save_to_parquet(df, file_path)
        return file_path

    def _get_file_path(self, arguments: dict[str, ArgType]) -> str:
        filtered_args = {k: v for k, v in arguments.items() if k not in self._skip_args}
        file_rel_path = self._path_template.format(**filtered_args)
        return os.path.join(self._cache_path, file_rel_path)

    def _get_temp_file_path(self, dirname: str) -> str:
        with tempfile.NamedTemporaryFile(
            suffix='.parquet.tmp', dir=dirname, delete=False
        ) as tmp_file:
            return tmp_file.name

    def _save_to_parquet(self, df: pd.DataFrame, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        dirname = os.path.dirname(path)
        temp_path = self._get_temp_file_path(dirname)
        try:
            df.to_parquet(temp_path)
            os.rename(temp_path, path)
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
