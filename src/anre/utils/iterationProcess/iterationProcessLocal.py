# mypy: disable-error-code="union-attr"
import dataclasses
import logging
import threading
import time
import traceback
from typing import Any

from anre.utils.functionsRunLog import FunctionsRunLog
from anre.utils.iterationProcess.config import Config


class IterationProcessLocal:
    """Reguliariai suka itaracijas vietiniame procese (naudojant threading)

    Sis objektas naudojamas kaip baze kitiems paveldeti

    Sio objekto tikslas:
    Kiek imanoma mandagiau uzdaryti procesa ir kiek galint greciau
    Gerai skaiciuoti laukimo laika
    Jei ivyko klaida praleisti valymosi funkcijas ir kartoti - pagal nustatymus.

    """

    ConfigCls = Config
    _nameDefault: str = "IterationProcessLocalBase"

    @classmethod
    def new(cls, name: str | None = None, **kwargs: Any):
        name = cls._nameDefault if name is None else name
        config = cls.ConfigCls(**kwargs)
        return cls(name=name, config=config)

    def __init__(self, name: str, config) -> None:
        assert isinstance(name, str)
        assert isinstance(config, self.ConfigCls)

        self.name = name
        self.functionsRunLog = FunctionsRunLog()

        self._config = config
        self._logger = logging.getLogger(f'bird.{self.__class__.__name__}.{self.name}')
        self._stop_event = threading.Event()
        self._stop_event.set()
        self._lastIterationStartTime = 0.0

        self._tryCount = 0
        self.__iterationTakesTimeMean = 0
        self._tooLongIterations_wasWarned = False
        self._job: threading.Thread | None = None

    def __str__(self):
        msg = "<{cls}` `{name}`>".format(cls=self.__class__.__name__, name=self.name)
        return msg

    def __del__(self):
        self.finish()
        self.stop()
        msg = "Stopped process `{}`".format(self.__str__())
        self._spreadMsg_info(msg)

    def get_config(self):
        return self._config

    def set_config(self, **kwargs: Any):
        newConfig = dataclasses.replace(self._config, **kwargs)
        self._config = newConfig

    def get_iterationTakesTimeMean(self) -> float:
        return self.__iterationTakesTimeMean

    def isAlive(self) -> bool:
        return self._job is not None and self._job.is_alive()

    def finish(self):
        self.stop(wait=True)
        self.run_inFinish()

    def stop(self, wait: bool = True):
        if not self._stop_event.is_set():
            msg = "Stopping `{cls}`, {waitStr}.".format(
                cls=self.__class__.__name__,
                waitStr="waiting till stop" if wait else "process will finish on its own",
            )
            self._spreadMsg_info(msg)
            self._stop_event.set()
            if wait:
                if self.isAlive():
                    self._job.join()
                assert not self.isAlive()

    def start(self, join: bool = False):
        assert not self.isAlive(), f'Process {self} is still alive.'

        msg = "Starting process `{}`".format(self.__str__())
        self._spreadMsg_info(msg)

        # issivalom
        assert self._stop_event.is_set()
        self._stop_event.clear()
        self._tryCount = 0

        self.run_beforeStart()

        ### start
        if join:
            # cia nedarom tikro join'o, tiesiog nekuriam thredo o normaliai executinam - taip debugeris veikia
            self._loop()
        else:
            self._job = threading.Thread(name=f'{self.__class__.__name__}._loop', target=self._loop)
            self._job.start()

    def join(self):
        if self.isAlive():
            self._job.join()

    def _interation_safe_withRetry(self):
        startTime = time.time()

        # filter, if we got to this place then it suppose to be stopped
        if self._stop_event.is_set():
            msg = f"Stop event is fired. We are not suppose to start new iteration, exiting (this can happen with low probability). Cls: `{self.__class__.__name__}`."
            self._spreadMsg_warning(msg)
            return None

        try:
            self.iteration()
            takesTime = time.time() - startTime
            self._tryCount = 0
        except BaseException as error:
            takesTime = time.time() - startTime
            self._tryCount += 1

            msgTmp = "Iteration in `{cls}.{obj}` failed (tryCount: {tryCount}). error: {error}; nextStep: {nextStep}; trace:\n{trace}\n"
            infoDict = dict(
                obj=self.name,
                cls=self.__class__.__name__,
                tryCount=self._tryCount,
                error=error.__repr__(),
                trace=traceback.format_exc(),
            )

            if self._tryCount > len(self._config.sleepInFailList) and not self._config.tryForever:
                nextStep = "Max try exceeded, the process will end after applying function `run_ifFinalFail`"
                infoDict['nextStep'] = nextStep
                msg = msgTmp.format(**infoDict)
                self._stop_event.set()
                self._spreadMsg_error(msg)
                try:
                    self.run_ifFinalFail(error=error)
                except BaseException as error:
                    msg = "Function `{cls}.{obj}.run_ifFinalFail` failed. Aborting operation. error: {error}; Trace: \n {trace} \n".format(
                        obj=self.name,
                        cls=self.__class__.__name__,
                        error=error.__repr__(),
                        trace=traceback.format_exc(),
                    )
                    self._spreadMsg_error(msg)
                return False

            else:
                if self._tryCount <= len(self._config.sleepInFailList):
                    sleepInFail = self._config.sleepInFailList[self._tryCount - 1]
                elif self._config.tryForever:
                    if self._config.sleepInFailList:
                        sleepInFail = self._config.sleepInFailList[-1]
                    else:
                        msg = f'tryForever is True, but sleepInFailList is empty. Not sure how long to sleep. Taking wait({self._config.wait}) value. But we should not get into this place, please provide sleepInFailList.'
                        self._spreadMsg_warning(msg)
                        sleepInFail = self._config.wait
                else:
                    raise AssertionError(
                        'We do not expect to land in this branch - please investigate.'
                    )

                nextStep = "Will continue with new attempt after applying function `run_ifTempFail` and sleeping for {sleepInFail} sec".format(
                    sleepInFail=sleepInFail
                )
                infoDict['nextStep'] = nextStep
                msg = msgTmp.format(**infoDict)
                self._spreadMsg_warning(msg)
                try:
                    self.run_ifTempFail(error=error)
                except BaseException as error:
                    msg = "Function `{cls}.{obj}.run_ifTempFail` failed. Aborting operation. error: {error}; Trace: \n {trace} \n".format(
                        obj=self.name,
                        cls=self.__class__.__name__,
                        error=error.__repr__(),
                        trace=traceback.format_exc(),
                    )
                    self._spreadMsg_error(msg)
                    self._stop_event.set()
                    return False

                time.sleep(sleepInFail)

        self.__iterationTakesTimeMean = 0.2 * takesTime + 0.8 * self.__iterationTakesTimeMean
        if (
            self.__iterationTakesTimeMean > self._config.wait
            and not self._tooLongIterations_wasWarned
        ):
            msg = "Itarciju vidurkis, tapo didesnis, nei wait config. Obj:{obj} - {objStr} ".format(
                obj=self.__class__.__name__,
                objStr=str(self),
            )
            self._spreadMsg_warning(msg)
            self._tooLongIterations_wasWarned = True

        return True

    def _loop(self):
        wait = self._config.wait
        _wait = 0.0
        while not self._stop_event.wait(_wait):
            self._lastIterationStartTime = time.time()

            self._interation_safe_withRetry()

            takesTime = time.time() - self._lastIterationStartTime
            if takesTime > self._config.wait:
                if self._lastIterationStartTime > 0:
                    self._spreadMsg_warning(
                        f'A single iteration is bigger then waitParam(`{self._config.wait}`): {takesTime=}'
                    )
            _wait = max(0.0, wait - takesTime)

    def _spreadMsg_info(self, msg: str):
        self._logger.info(msg)

    def _spreadMsg_warning(self, msg: str):
        self._logger.warning(msg)

    def _spreadMsg_error(self, msg: str):
        self._logger.error(msg)

    ##### funkcijos skirtos overridinimui #####

    def run_beforeStart(self):
        """"""
        pass

    def run_inFinish(self):
        """"""
        pass

    def run_ifTempFail(self, error: BaseException, *args: Any, **kwargs: Any):
        """Funkija kuri bus paleista uzluzus vienai iteraciai, bet dar veliau bandyzime"""
        msg = f'Error: {error.__repr__()}'
        print(msg)
        self._spreadMsg_error(msg)

    def run_ifFinalFail(self, error: BaseException, *args: Any, **kwargs: Any):
        """Funkcija, kuri bus paleista galutinai uzlyzus"""
        msg = f'Error: {error.__repr__()}'
        print(msg)
        self._spreadMsg_error(msg)

    def iteration(self):
        """
        The function that is run in process.

        This function shoud take care all the thing you need to be done.

        Be default this function calls a named function according to state.
        In this way you can actualy call any functionand event have a whole nes of functions.
        """
        self.functionsRunLog.runFunction(self._print_dummyMsg, '_print_dummyMsg')

    def _print_dummyMsg(self):
        print(
            "Iteration function. Just printing this message. It would be reasonable to override iteration function."
        )
