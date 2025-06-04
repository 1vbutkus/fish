import copy


class ConstGenerator:
    @classmethod
    def new(cls, baseParam: dict | list) -> 'ConstGenerator':
        return cls(
            baseParam=baseParam,
        )

    def __init__(self, baseParam: dict | list) -> None:
        assert isinstance(baseParam, (dict, list))
        self.baseParam: dict | list = baseParam

    def __next__(self):
        return self.sample()

    def __iter__(self):
        return self

    def sample(self) -> dict | list:
        return copy.deepcopy(self.baseParam)
