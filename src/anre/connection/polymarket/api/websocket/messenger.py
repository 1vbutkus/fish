from collections import deque

from anre.utils.functions import yield_popleft


class Messenger:
    def __init__(self):
        self._deque: deque = deque()

    def put(self, message: dict):
        self._deque.append(message)

    def get_pop_messages(self) -> list[dict]:
        return list(yield_popleft(self._deque))

    def get_peek_messages(self) -> list[dict]:
        return list(self._deque)
