from dataclasses import asdict, dataclass

import numpy as np

from anre.utils.dataclass_type_validator import dataclass_validate


class _TableBase:
    def __repr__(self) -> str:
        fieldStrList = []
        for fieldName, value in self.__dict__.items():
            if not fieldName.startswith('_'):
                if isinstance(value, np.ndarray):
                    valueStr = (
                        np.array_repr(value, precision=4)
                        .replace('\n', '')
                        .replace(' ', '')
                        .replace(',', ', ')
                    )
                else:
                    valueStr = str(value)
                resStr = f'    {fieldName}={valueStr},'
                fieldStrList.append(resStr)
        fieldStrJoined = '\n'.join(fieldStrList)
        return f'{self.__class__.__name__}(\n{fieldStrJoined}\n)'

    def _validate_dimensionsAndTypes(self):
        lenSet = set()
        for fieldName, value in self.__dict__.items():
            if not fieldName.startswith('_'):
                assert isinstance(value, (np.ndarray, list, tuple))
                lenSet.add(len(value))

        assert len(lenSet) == 1


@dataclass_validate(strict=True)
@dataclass(frozen=False, repr=False)
class TableBaseMutable(_TableBase):
    """Musu lenteles bazine klase.

    Paskirtis:
        Uztikrina, kad lentele tikrai yra lentele t.y. visi fieldai yra np.ndarray ir vienodo ilgio
        Duoda padoru printa
    """

    def to_dict(self) -> dict[str, np.ndarray]:
        return asdict(self)

    def __post_init__(self):
        self._validate_dimensionsAndTypes()


@dataclass(frozen=True, repr=False)
class TableBaseFrozen(_TableBase):
    """Musu lenteles bazine klase.

    Paskirtis:
        Uztikrina, kad lentele tikrai yra lentele t.y. visi fieldai yra np.ndarray|list|tuple ir vienodo ilgio
        Duoda padoru printa
    """

    def to_dict(self) -> dict[str, np.ndarray]:
        return asdict(self)

    def __post_init__(self):
        self._validate_dimensionsAndTypes()
