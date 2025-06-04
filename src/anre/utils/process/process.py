import datetime
import os
import subprocess
from typing import Callable


class Process:
    @classmethod
    def get_processCreatedDateTime(cls, pid: int) -> datetime.datetime:
        lastAccTsStr = subprocess.check_output(f'stat /proc/{pid} --format=%x', shell=True).decode()
        lastModTsStr = subprocess.check_output(f'stat /proc/{pid} --format=%y', shell=True).decode()
        lastChaTsStr = subprocess.check_output(f'stat /proc/{pid} --format=%z', shell=True).decode()
        assert lastAccTsStr == lastModTsStr == lastChaTsStr, (
            'we assume that these timestamps are always equal for process metadata'
        )
        return datetime.datetime.strptime(lastAccTsStr[:26], '%Y-%m-%d %H:%M:%S.%f')

    @classmethod
    def run_withLiveOutput(
        cls,
        command: str,
        cwd: str | None = None,
        consumeMsgFn: Callable | None = None,
        raiseIfError: bool = True,
        timeoutSec: float | None = None,
    ) -> int:
        cwd = cwd if cwd else os.getcwd()
        consumeMsgFn = consumeMsgFn if consumeMsgFn is not None else lambda msg: None
        assert callable(consumeMsgFn)  # type: ignore[arg-type]

        process = subprocess.Popen(
            ['/bin/bash', '-c', command], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        assert process.stdout
        with process.stdout:
            for line in iter(process.stdout.readline, b''):  # b'\n'-separated lines
                consumeMsgFn(line)
        returnValue = process.wait(timeout=timeoutSec)  # 0 means success

        if returnValue != 0 and raiseIfError:
            raise OSError(
                f'running {command=} failed with {returnValue=}, check log for error message'
            )

        return returnValue
