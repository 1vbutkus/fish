# mypy: disable-error-code="assignment"
from typing import Any

import numpy as np
import pandas as pd


class Eval:
    @classmethod
    def eval(cls, df: pd.DataFrame, expr: str, resolvers: tuple[Any] = (), **kwargs: Any) -> Any:
        assert isinstance(resolvers, (list, tuple))
        resolvers = list(resolvers) + [cls._get_defaultResolver()] + [dict(df)]
        locals = {k: v for d in resolvers for k, v in d.items()}
        return eval(expr, None, locals)

    @classmethod
    def get_fieldSr(cls, df: pd.DataFrame, field: str, resolvers=()) -> pd.Series:
        resSr = cls.eval(df=df, expr=field, resolvers=resolvers)
        assert isinstance(resSr, pd.Series)
        return resSr.copy()

    @staticmethod
    def _get_defaultResolver() -> dict:
        return dict(
            clip=pd.Series.clip,
            minimum=np.minimum,
            maximum=np.maximum,
            quantile=pd.Series.quantile,
        )
