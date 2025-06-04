import abc

import numpy as np
import pandas as pd


class IType(abc.ABC):
    @abc.abstractmethod
    def is_type(self, sr: pd.Series) -> bool: ...

    @abc.abstractmethod
    def to_type(self, sr: pd.Series) -> pd.Series: ...

    @abc.abstractmethod
    def get_name(self) -> str: ...


class Numpy(IType):
    def __init__(self, numpyType: np.dtype) -> None:
        assert 'numpy.dtype' in str(type(numpyType)) or type(numpyType) is type
        # assert type(numpyType) == np.dtype or type(numpyType) == type
        self._type = numpyType

    def is_type(self, sr: pd.Series) -> bool:
        return sr.dtype == self._type

    def to_type(self, sr: pd.Series) -> pd.Series:
        return sr.astype(self._type)

    def get_name(self) -> str:
        return str(self._type)


class Pandas(IType):
    def __init__(self, pandasType: type) -> None:
        assert type(pandasType) is type
        self._type = pandasType()  # pd types need to be instantiated

    def is_type(self, sr: pd.Series) -> bool:
        return sr.dtype == self._type

    def to_type(self, sr: pd.Series) -> pd.Series:
        return sr.astype(self._type)

    def get_name(self) -> str:
        return str(self._type)


class Bool(IType):
    def __init__(self) -> None:
        self._type = Numpy(np.bool_)  # type: ignore[arg-type]

    def is_type(self, sr: pd.Series) -> bool:
        return self._type.is_type(sr=sr)

    def to_type(self, sr: pd.Series) -> pd.Series:
        return self._type.to_type(sr=sr)

    def get_name(self) -> str:
        return self._type.get_name()


class DateTime64(IType):
    def __init__(self) -> None:
        self._type = Numpy(np.datetime64(0, 'ns').dtype)

    def is_type(self, sr: pd.Series) -> bool:
        return self._type.is_type(sr=sr)

    def to_type(self, sr: pd.Series) -> pd.Series:
        if isinstance(sr.dtype, pd.DatetimeTZDtype):
            sr = sr.dt.tz_localize(None)
        return self._type.to_type(sr=sr)

    def get_name(self) -> str:
        return self._type.get_name()


class Float64(IType):
    def __init__(self) -> None:
        self._type = Numpy(np.float64)  # type: ignore[arg-type]

    def is_type(self, sr: pd.Series) -> bool:
        return self._type.is_type(sr=sr)

    def to_type(self, sr: pd.Series) -> pd.Series:
        return self._type.to_type(sr=sr)

    def get_name(self) -> str:
        return self._type.get_name()


class Int64(IType):
    def __init__(self) -> None:
        self._type = Numpy(np.int64)  # type: ignore[arg-type]

    def is_type(self, sr: pd.Series) -> bool:
        return self._type.is_type(sr=sr)

    def to_type(self, sr: pd.Series) -> pd.Series:
        return self._type.to_type(sr=sr)

    def get_name(self) -> str:
        return self._type.get_name()


class Int64NA(IType):
    def __init__(self) -> None:
        self._type = Pandas(pd.Int64Dtype)

    def is_type(self, sr: pd.Series) -> bool:
        return self._type.is_type(sr=sr)

    def to_type(self, sr: pd.Series) -> pd.Series:
        return self._type.to_type(sr=sr)

    def get_name(self) -> str:
        return self._type.get_name()


class String(IType):
    def is_type(self, sr: pd.Series) -> bool:
        return sr.dtype.type == np.object_ and sr.map(lambda x: type(x) is str).all()

    def to_type(self, sr: pd.Series) -> pd.Series:
        return sr.astype(str)

    def get_name(self) -> str:
        return "numpy.object_ (string)"


class TimeDelta64(IType):
    def __init__(self) -> None:
        self._type = Numpy(np.timedelta64(0, 'ns').dtype)

    def is_type(self, sr: pd.Series) -> bool:
        return self._type.is_type(sr=sr)

    def to_type(self, sr: pd.Series) -> pd.Series:
        return self._type.to_type(sr=sr)

    def get_name(self) -> str:
        return self._type.get_name()


class Object(IType):
    def is_type(self, sr: pd.Series) -> bool:
        return isinstance(sr.dtype, np.dtypes.ObjectDType)

    def to_type(self, sr: pd.Series) -> pd.Series:
        return sr

    def get_name(self) -> str:
        return "object"


all_type_classes: list[type[IType]] = [
    DateTime64,
    TimeDelta64,
    Float64,
    Object,
    Int64,
    Int64NA,
    String,
    Bool,
]
