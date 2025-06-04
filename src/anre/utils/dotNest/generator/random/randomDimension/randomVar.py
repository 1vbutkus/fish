from anre.utils.dotNest.generator.random.randomDimension.creator import Creator
from anre.utils.dotNest.generator.random.randomDimension.iRandomDimension import IRandomDimension


class RandomVar:
    """Placehoderis baseParam'e, kuris pasako, kad konkreciai sita reiksme bus randomizuota"""

    @classmethod
    def new_choice(cls, elems):
        return cls(
            dtype='choice',
            elems=elems,
        )

    @classmethod
    def new_int(cls, center: int | float, scale: int | float, hardLims=None):
        return cls(
            dtype='int',
            center=center,
            scale=scale,
            hardLims=hardLims,
        )

    @classmethod
    def new_float(cls, center: int | float, scale: int | float, hardLims=None):
        return cls(
            dtype='float',
            center=center,
            scale=scale,
            hardLims=hardLims,
        )

    def __init__(self, dtype: str, *, elems=None, center=None, scale=None, hardLims=None) -> None:
        assert dtype in ['choice', 'float', 'int']
        if dtype == 'choice':
            assert elems is not None
            assert isinstance(elems, (list, tuple))
            assert elems

            assert center is None
            assert scale is None
            assert hardLims is None

        elif dtype in ['float', 'int']:
            assert elems is None
            assert center is not None

        else:
            raise NotImplementedError

        self.dtype: str = dtype
        self.elems = elems
        self.center = center
        self.scale = scale
        self.hardLims = hardLims

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(dtype={self.dtype}, elems={self.elems}, center={self.center}, scale={self.scale}, hardLims={self.hardLims})'

    def get_randomDimension(self, dotPath: str) -> IRandomDimension:
        return Creator.new(
            dotPath=dotPath,
            dtype=self.dtype,
            elems=self.elems,
            center=self.center,
            scale=self.scale,
            hardLims=self.hardLims,
        )
