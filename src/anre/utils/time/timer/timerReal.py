import datetime
import json as json
import logging
import os.path
import time

import ntplib

from anre.utils.decorators import singleton
from anre.utils.fileSystem import FileSystem
from anre.utils.time.timer.iTimer import ITimer


@singleton
class TimerReal(ITimer, object):
    is_real = True
    wasSinc = False
    offsetSec = 0
    offsetDt = datetime.timedelta()
    osCacheDir = FileSystem.create_os_cache_dir('fish', 'timer')
    cacheFile = os.path.join(osCacheDir, '_cache_timer.json')

    def __init__(self):
        self.update()

    @classmethod
    def update(cls, force=False):
        cls.offsetSec = cls._get_offset(force=force)
        cls.offsetDt = datetime.timedelta(seconds=cls.offsetSec)

    @classmethod
    def _get_offset(cls, force=False):
        if cls.wasSinc and not force:
            return cls.offsetSec
        else:
            if not force and os.path.isfile(cls.cacheFile):
                try:
                    with open(cls.cacheFile, 'r') as outfile:
                        data = json.load(outfile)

                    if data['nowS'] > time.time() - 60 * 60:
                        offsetSec = data['offsetSec']
                        cls.wasSinc = True
                        return offsetSec

                except ValueError:
                    os.remove(cls.cacheFile)

            try:
                client = ntplib.NTPClient()
                response = client.request('pool.ntp.org')
                # response = client.request('europe.pool.ntp.org')
                # response = client.request('212.59.0.2')
                offsetSec = response.offset

                print("sinc with pool.ntp.org")

                # cache
                data = {'offsetSec': offsetSec, 'nowS': time.time()}
                with open(cls.cacheFile, 'w') as outfile:
                    json.dump(data, outfile)

                cls.wasSinc = True
                return offsetSec

            except BaseException:
                msg = "Failed to sink time."
                try:
                    logger = logging.getLogger(__name__)
                except BaseException:
                    logger = logging.getLogger('')
                logger.warning(msg)
                print(msg)
                return cls.offsetSec

    def nowDt(self, offset=0.0) -> datetime.datetime:
        return datetime.datetime.utcnow() + self.offsetDt + datetime.timedelta(seconds=offset)

    def nowS(self, offset=0.0) -> float:
        return time.time() + self.offsetSec + offset
