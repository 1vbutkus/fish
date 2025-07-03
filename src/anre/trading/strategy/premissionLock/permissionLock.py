from threading import Lock
from typing import Dict, Optional, Set


class PermissionLock:
    """Nurodo ka strategija gali daryti o ko ne.

    By default, it is NORMAL-TRADE
    """

    _backoffLevel = 40

    _valueMapToStr: Dict[int, str] = {
        0: 'NORMAL-TRADE',
        10: 'CANCEL-CLOSE-ONLY',  # it can cancel all, place only that potential closes the position
        20: 'CANCEL-ONLY',  # only cancel is allowed
        30: 'SUSPEND',  # do not allow any action to be executed
        _backoffLevel: 'BACKOFF',  # actively cancel all, do not place anything and make sure re-cancel if needed
    }

    def __init__(self, allowedValues: Optional[Set[int]] = None):
        assert allowedValues is None or isinstance(allowedValues, set)

        self._changeLock = Lock()
        self._lockDict: Dict[str, int] = {}
        self._allowedValues: Optional[Set[int]] = allowedValues

    def get_currentValueInt(self) -> int:
        valueInt = max(self._lockDict.values(), default=0)
        return valueInt

    def get_currentValueStr(self) -> str:
        valueInt = max(self._lockDict.values(), default=0)
        return self.get_valueStr_fromInt(valueInt)

    def register_levelMap(self, valueInt: int, valueStr: str):
        assert isinstance(valueInt, int)
        assert isinstance(valueStr, str)
        assert valueInt not in self._valueMapToStr, 'valueInt is already registered'
        self._valueMapToStr[valueInt] = valueStr

    def get_valueStr_fromInt(self, valueInt: int) -> str:
        if valueInt in self._valueMapToStr:
            return self._valueMapToStr[valueInt]
        else:
            assert isinstance(valueInt, int)
            return str(valueInt)

    def put_lock(self, valueInt: int, owner: str, override: bool = False):
        assert isinstance(valueInt, int)
        assert isinstance(owner, str)
        assert 0 <= valueInt <= 40, f'valueInt must be in [0, 40], got {valueInt}'

        with self._changeLock:
            if override:
                self._lockDict[owner] = valueInt
            else:
                assert owner not in self._lockDict, (
                    'owner is already have lock, use override=True or release_lock'
                )
                self._lockDict[owner] = valueInt

    def put_lock_backoff(self, owner: str, override: bool = False):
        self.put_lock(valueInt=self._backoffLevel, owner=owner, override=override)

    def release_lock(self, owner: str, raiseIfMissing: bool = True):
        with self._changeLock:
            if raiseIfMissing:
                assert owner in self._lockDict, f'Owner do not have the lock {owner=}'
                del self._lockDict[owner]
            else:
                try:
                    del self._lockDict[owner]
                except KeyError:
                    pass

    def sudo_releaseAll(self):
        """Visus uzraktus atrakina

        Nieko netrinam tik replasinam reiksmes i 0
        Netrinam, nes procesai gali noreti nusimtisavo orginalius lockus ir gausim klaidas
        """
        with self._changeLock:
            for owner in list(self._lockDict.keys()):
                self._lockDict[owner] = 0


def __dummy__():
    self = PermissionLock()

    self.register_levelMap(5, 'AAA')
    self._get_valueStr(5)
    self._get_valueStr(9)
