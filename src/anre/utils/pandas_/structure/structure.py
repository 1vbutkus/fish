from anre.utils.pandas_.structure.column.column import Column
from anre.utils.pandas_.structure.dataframe.dataframe import DataFrame
from anre.utils.pandas_.structure.index.index import Index
from anre.utils.pandas_.structure.series.series import Series


class Structure:
    @classmethod
    def validate(cls, localsDict: dict):
        for name, object in localsDict.items():
            if type(object) is Index:
                prefix = ''
            elif type(object) is Column:
                prefix = ''
            elif type(object) is DataFrame:
                prefix = 'df_'
            elif type(object) is Series:
                prefix = 'sr_'
            else:
                continue

            assert name.startswith(prefix), (
                f'{object=} python name should start with \'{prefix}\' but is {name=}'
            )
            objName = object.get_name() if object.get_name() is not None else 'none_index'
            objNamePy = name[len(prefix) :]
            assert objNamePy == objName.replace('.', '_'), (
                f'{object=} python name should be {objName} but is {objNamePy}'
            )
