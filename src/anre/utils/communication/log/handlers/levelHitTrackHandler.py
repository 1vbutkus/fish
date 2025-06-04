from logging import ERROR, Handler, getLogger


class LevelHitTrackHandler(Handler):
    fired = False

    def __init__(self, level=ERROR, logger='', install: bool = True) -> None:
        super().__init__()
        self.level = level
        self.logger = logger
        if install:
            self.install()

    def install(self) -> None:
        self.setLevel(self.level)
        getLogger(self.logger).addHandler(self)

    def emit(self, record) -> None:
        self.fired = True

    def reset(self) -> None:
        self.fired = False

    def remove(self) -> None:
        getLogger().removeHandler(self)
