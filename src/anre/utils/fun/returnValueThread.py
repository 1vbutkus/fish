import sys
import threading
from typing import Any


class ReturnValueThread(threading.Thread):
    # FIXME: rewrite API to not model is-a relationship
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.result = None

    def run(self) -> None:
        if self._target is None:  # type: ignore[attr-defined]
            return  # could alternatively raise an exception, depends on the use case
        try:
            self.result = self._target(*self._args, **self._kwargs)  # type: ignore[attr-defined]
        except Exception as exc:
            print(f'{type(exc).__name__}: {exc}', file=sys.stderr)  # properly handle the exception

    def join(self, *args: Any, **kwargs: Any) -> None:
        super().join(*args, **kwargs)
        return self.result
