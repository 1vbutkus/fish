from dataclasses import dataclass

import numpy as np
import pandas as pd
from dacite import UnexpectedDataError

from anre.utils import testutil
from anre.utils.dataclass_type_validator import dataclass_validate
from anre.utils.dataStructure.general import GeneralBaseFrozen, GeneralBaseMutable


class TestGeneralBase(testutil.TestCase):
    def test_smoke_happyPath(self) -> None:
        # simple mutable case
        @dataclass_validate
        @dataclass(repr=False)
        class Foo(GeneralBaseMutable):
            a: int
            b: float

        foo1 = Foo(a=1, b=2.0)
        foo2 = foo1.set(b=10.0)
        foo1.a = 5
        dict_ = foo1.to_dict()
        foo3 = Foo.from_dict(dict_)

        assert foo1 == foo1
        assert not foo1 == foo2
        assert foo1 == foo3

        # nested complexfrozen case
        @dataclass_validate
        @dataclass(repr=False, frozen=True)
        class Bar(GeneralBaseFrozen):
            foo1: Foo
            foo2: Foo
            x: int
            df: pd.DataFrame
            dictValue: dict
            listValue: list
            arr: np.ndarray

        df = pd.DataFrame({'a': [1, 2], 'b': ['x', 'y']})
        bar1 = Bar(
            foo1=foo1,
            foo2=foo2,
            x=5,
            df=df,
            dictValue={'a': 1},
            listValue=[1, 2],
            arr=np.array([1, 2]),
        )
        barDict = bar1.to_dict()

        with self.assertRaises(BaseException):
            _ = Bar.from_dict(barDict)

        bar2 = Bar.new_fromNestDict(barDict)
        assert bar1.get_hash() == bar2.get_hash()

        barDict['extra'] = 1
        with self.assertRaises(UnexpectedDataError):
            _ = Bar.new_fromNestDict(barDict)

    def test_nestedCase(self) -> None:
        @dataclass(frozen=True, repr=False)
        class ConfigTest0(GeneralBaseFrozen):
            a: int
            b: float

        @dataclass_validate
        @dataclass(frozen=True, repr=False)
        class ConfigTest1(GeneralBaseFrozen):
            a: int
            configTest0: ConfigTest0

        _ = ConfigTest1.new_fromNestDict({'a': 1, 'configTest0': {'a': 2, 'b': 3}})

    def test_update(self) -> None:
        @dataclass(frozen=True, repr=False)
        class ConfigTest(GeneralBaseFrozen):
            a: int
            b: float

        config0 = ConfigTest(a=1, b=2.0)

        config1 = config0.new_update(b=3.0)
        assert type(config1) is type(config0)

        with self.assertRaises(UnexpectedDataError):
            config1.new_update(c='a')
