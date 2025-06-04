# mypy: disable-error-code="func-returns-value,"
import _pickle as pkl
import datetime
import hashlib
import itertools
import random
import re
import string
import threading
from collections import defaultdict, deque
from collections.abc import Iterable
from typing import Any, Generator

import numpy as np
import pandas as pd

strOrDatetimeT = str | datetime.datetime | None
Table = np.ndarray | pd.DataFrame

_clearPattern = re.compile(r'[\W]+', re.UNICODE)


def sequentialIdGenerator(maxValue: int | None = None) -> Generator[int, None, None]:
    lock = threading.Lock()
    if maxValue is not None:
        assert maxValue > 1
        assert isinstance(maxValue, int)

    internalId: int = -1
    while True:
        with lock:
            internalId += 1
            if maxValue:
                internalId = internalId % maxValue
            yield internalId


def clean_strToAlphanumericOnly(inputStr: str, replace='') -> str:
    return _clearPattern.sub(replace, inputStr)


def identity(x):
    return x


def clip(x, low, up):
    return max(min(x, up), low)


def check_isAllUnique(x) -> bool:
    seen = set()
    return not any(i in seen or seen.add(i) for i in x)


def mapRange(oldValue, oldMin, oldMax, newMin, newMax):
    oldValue = clip(oldValue, oldMin, oldMax)
    oldRange = oldMax - oldMin
    if oldRange == 0:
        newValue = newMin
    else:
        newRange = newMax - newMin
        newValue = (((oldValue - oldMin) * newRange) / oldRange) + newMin
    return newValue


def seqNr(sr: pd.Series) -> pd.Series:
    """Suskiaciuoja kiek laiko prabuna stabilioje busenoje"""
    # sr = pd.Series([0,0,1,1,1,0,1,0,1,0,0,0,1,1])

    breakPoints = (sr != sr.shift(1).values).values
    seqFull = np.arange(len(breakPoints))
    seqSteps = np.zeros(len(breakPoints), dtype=np.int64)
    seqSteps[breakPoints] = seqFull[breakPoints]  # type: ignore
    seqSteps = np.maximum.accumulate(seqSteps)
    seqNrAr = seqFull - seqSteps
    seqNrSr = pd.Series(seqNrAr, index=sr.index)
    return seqNrSr


def revSeqNr(sr: pd.Series) -> pd.Series:
    return seqNr(sr=sr.iloc[::-1]).iloc[::-1]


def ifNull(value, default):
    if value is None or pd.isnull(value):
        return default
    return value


def logit(p):
    return np.log(p / (1 - p))


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def lineParamsFromPoints(x1, x2, y1, y2) -> tuple[float, float]:
    """Suranda tiesiones funkcijos y(x) = a + b*x parameturs a ir b"""
    assert x1 != x2
    b = (y1 - y2) / (x1 - x2)
    a = y1 - b * x1
    return a, b


def clipAndFillNaArr(
    x: np.ndarray, x_min: float = 0, x_max: float = 1, nan: float = 0
) -> np.ndarray:
    """Vektroiu auriboja iruzpido na/inf reikemse"""
    x = np.clip(x, a_min=x_min, a_max=x_max)
    x = np.nan_to_num(x, copy=False, nan=nan, posinf=x_max, neginf=x_min)
    return x


def clipValue(x: float | int, lower=None, upper=None) -> int | float:
    if lower is not None and x < lower:
        x = lower
    if upper is not None and x > upper:
        x = upper
    return x


def sortOrder(x) -> list:
    return sorted(range(len(x)), key=x.__getitem__)


def isMonotonicIncreasing(x) -> bool:
    return all(x[i] <= x[i + 1] for i in range(len(x) - 1))


def checksum(data) -> str:
    if isinstance(data, dict):
        data = [(x, y) for x, y in sorted(data.items())]
    return hashlib.md5(pkl.dumps(data)).hexdigest()


def compareDictsByKeys(aDic: dict, bDict: dict) -> dict:
    resDict = {}
    for key in set(aDic.keys()) | set(bDict.keys()):
        isEq = checksum(aDic.get(key)) == checksum(bDict.get(key))
        resDict[key] = isEq
    return resDict


def poundArr(arr):
    """Sugruda masyva per viena pozicija.

    [1,2,3,4] -> [0, 1, 2, 7]

    """
    ans = np.roll(arr, 1)
    ans[-1] = ans[-1] + ans[0]
    ans[0] = 0
    return ans


def shiftArr(arr, fill=np.nan):
    """Pastumia masyva per viena pozicija.

    [1,2,3,4] -> [0, 1, 2, 3]

    """
    ans = np.roll(arr, 1)
    ans[0] = fill
    return ans


def relu(x):
    return np.maximum(0, x)


def get_randomStr(length=16) -> str:
    return ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def get_randomWord(length=16) -> str:
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def chunks(x, n=None):
    """Yield successive n-sized chunks from l."""

    if n is None:
        yield x
    else:
        for i in range(0, len(x), n):
            yield x[i : i + n]


def chunksTable(table: Table, chunkSize=None):
    if isinstance(table, pd.DataFrame):
        if chunkSize is None:
            yield table
        else:
            for i in range(0, table.shape[0], chunkSize):
                yield table.iloc[i : (i + chunkSize)]

    elif isinstance(table, np.ndarray):
        if chunkSize is None:
            yield table
        else:
            for i in range(0, table.shape[0], chunkSize):
                yield table[i : (i + chunkSize)]

    else:
        raise NotImplementedError


def diff_list(a: list | tuple | pd.Series | pd.Index, b: list | tuple | set | pd.Series | pd.Index):
    setB = set(b)
    return [val for val in a if val not in setB]


def flattenList(listList: Iterable[list]) -> list:
    return [item for sublist in listList for item in sublist]


def mergeDict(dictList: list[dict]) -> dict:
    return {k: v for d in dictList for k, v in d.items()}


def groupByList(list_: Iterable, by: Iterable) -> dict[Any, list]:
    defDict = defaultdict(list)
    for idx, val in zip(by, list_):
        defDict[idx].append(val)
    return dict(defDict)


def mergeDictList(dictList: list[dict]) -> dict:
    return {k: v for d in dictList for k, v in d.items()}


def compareWithNa(a, b):
    return (a == b) | ((a != a) & (b != b))


def where(boolList: list[bool]):
    return [i for i, elem in enumerate(boolList, 0) if elem]


def get_dfSummary(df: pd.DataFrame) -> pd.DataFrame:
    """Returns the summary of DataFrame"""

    resList = []
    for field, ser in df.items():
        serUn = ser.unique()
        countNa = ser.isnull().sum()
        prNa = round(countNa / ser.shape[0], 3)
        dtype = ser.dtype.name
        try:
            minVal = ser.min()
            maxVal = ser.max()
        except BaseException:
            minVal = np.nan
            maxVal = np.nan

        example = ','.join([str(el) for el in serUn[:100]])[:150]
        res = (field, dtype, len(serUn), countNa, prNa, minVal, maxVal, example)
        resList.append(res)

    resDf = pd.DataFrame(
        resList, columns=['field', 'dtype', '#unique', '#NA', 'prNa', 'min', 'max', 'example']
    )

    return resDf


def get_robustOutlierLims(sr: pd.Series, qv=0.2, sigma=1.0):
    """Get limits of outlier definition

    The parameters to standar normal distribution:
        0.1, 1 -> 2.27
        0.1, 1.5 -> 2.77
        0.1, 1.5 -> 3.27

        0.1, 1 -> 2.27
        0.05, 1 -> 2.64
        0.02, 1 -> 3.05
    """

    assert 0 <= qv <= 1
    assert 0 <= sigma
    stdVal = sr.std()
    lim1 = sr.quantile(qv) - sigma * stdVal
    lim2 = sr.quantile(1 - qv) + sigma * stdVal
    return lim1, lim2


def get_expand_grid_gnr(**items):
    names = items.keys()
    vals = items.values()
    for res in itertools.product(*vals):
        yield dict(zip(names, res))


def yield_popleft(dequeObj: deque, n=None):
    """Svarus ir ekonomiskas elementu panaudojimas isvalant su pop

    Jei, reikia panaudoti obj elementus ir iskarto svariai isvalyti, tai
    geriau naudoti sia funkcija

    Args:
        dequeObj: deque
        n: kiek elementu paimti, jei None, tai paima kvietimo momentu esani ilgi.

    Example:
        dequeObj = deque('abc')
        list(yield_popleft(dequeObj))
    """
    assert isinstance(dequeObj, deque), f'Expected deque object, but got {type(dequeObj)}'

    if n is None:
        while True:
            if dequeObj:
                try:
                    yield dequeObj.popleft()
                except IndexError:
                    break
                except BaseException as e:
                    raise e
            else:
                break
    else:
        for i in range(n):
            if dequeObj:
                try:
                    yield dequeObj.popleft()
                except IndexError:
                    break
                except BaseException as e:
                    raise e
            else:
                break


def convert_x2npArray(x, dtype=None) -> np.ndarray:
    if isinstance(x, (pd.Series, pd.Index)):
        # first we try values, because it is faster
        tx = x.values
        if not isinstance(tx, np.ndarray):
            tx = x.to_numpy()
    elif isinstance(x, pd.api.extensions.ExtensionArray):
        tx = x.to_numpy()
    elif isinstance(x, np.ndarray):
        tx = x
    elif isinstance(x, Iterable):
        tx = pd.array(np.array(x), dtype=dtype).to_numpy()  # type: ignore[arg-type]
    else:
        raise NotImplementedError(f"Not implemented type `{type(x)}`")

    assert isinstance(tx, np.ndarray)
    return tx


def convert_y2expectedObj(y, x):
    # define return object
    if isinstance(x, pd.Series):
        return pd.Series(y, index=x.index)
    elif isinstance(x, pd.Index):
        return pd.Series(y, index=x)
    elif isinstance(x, Iterable):
        return y
    else:
        raise NotImplementedError(f"Not implemented type `{type(x)}`")
