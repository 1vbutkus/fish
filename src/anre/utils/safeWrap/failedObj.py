from typing import Any


class FailedObj:
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return True
        return False

    def __repr__(self) -> str:
        return 'FailedObj()'
