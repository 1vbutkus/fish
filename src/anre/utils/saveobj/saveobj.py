"""Module dedicated for fast or efective objects saving

It is based on pickle and gzip.

The modele is needed for the folowing reasons:
    I turns out that pickle works well with gzip that allos to save a lot of space.
    The build in pickle in pandas_ is not perfect since the category atributs are lost
    Convinience

"""

import _pickle as pickle
import bz2
import errno
import gzip
import os
import random
import shutil
import string
from typing import Any

import pandas as pd

from anre.utils.Json.Json import Json


def get_randomStr(length=16) -> str:
    return ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def gzipFile(path, delSource: bool = False):
    """Suspaudzia viena faila i gz formata

    Pasirupina, kad faile nebutu jokios dir strukturos - taip pandas_ gali nuskaityti iskarto duomenis.
    Issaugojo toje pacioje vietoje kur randa sourcefile

    Grazina naujo failo path
    """
    # filePath = outPath_csv

    ### pasirupina path'asi
    if not os.path.exists(path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

    out_path = path + '.gz'
    with open(path, 'rb') as f_in:
        with gzip.open(out_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    if delSource:
        try:
            os.remove(path)
        except Exception:
            print("File `{filePath}` was not removed, because error.".format(filePath=path))

    return out_path


def dump(obj, path, overwrite: bool = False, **kwargs: Any):
    """Konkretus objektas i konkretu faila

    Jei filePath galune turi pletini '.gz' arba '.bz2', tai objektas iskarto ir archyvuojamas.
    Kitu atveju naudojamas tieisog pickle

    """

    if os.path.exists(path) and not overwrite:
        msg = f'File already exist. Use overwrite=True if needed: {path}'
        raise FileExistsError(msg)

    # use temp file
    file_path_name, file_extension = os.path.splitext(path)
    _, file_extension_deeper = os.path.splitext(file_path_name)
    temp_file_path = f'{file_path_name}_temp_{get_randomStr(16)}{file_extension}'

    if file_extension == '.gz':
        if file_extension_deeper == '.json':
            Json.dump(obj=obj, path=temp_file_path, archive=True, **kwargs)
        elif file_extension_deeper == '.jsonl':
            Json.linesDump(objList=obj, path=temp_file_path, archive=True, **kwargs)
        elif file_extension_deeper == '.parquet':
            assert isinstance(obj, pd.DataFrame), (
                f'Only pd.Dataframe can by used for parquet, but got {type(obj)}'
            )
            if 'compression' in kwargs:
                assert kwargs['compression'] == 'gzip'
                _ = kwargs.pop('compression')
            obj.to_parquet(temp_file_path, compression='gzip', **kwargs)

        else:
            objDumps = pickle.dumps(obj)
            with gzip.open(temp_file_path, 'wb') as fh:
                fh.write(objDumps)

    elif file_extension == '.bz2':
        if file_extension_deeper == '.json':
            Json.dump(obj=obj, path=temp_file_path, archive=True, **kwargs)
        elif file_extension_deeper == '.jsonl':
            Json.linesDump(objList=obj, path=temp_file_path, archive=True, **kwargs)
        else:
            objDumps = pickle.dumps(obj)
            with bz2.BZ2File(temp_file_path, 'wb') as fh:
                fh.write(objDumps)

    elif file_extension == '.pkl':
        with open(temp_file_path, "wb") as fh:
            pickle.dump(obj, fh)

    elif file_extension == '.parquet':
        assert isinstance(obj, pd.DataFrame), (
            f'Only pd.Dataframe can by used for parquet, but got {type(obj)}'
        )
        obj.to_parquet(temp_file_path, **kwargs)

    elif file_extension == '.json':
        Json.dump(obj=obj, path=temp_file_path, **kwargs)

    elif file_extension == '.jsonl':
        Json.linesDump(objList=obj, path=temp_file_path, **kwargs)

    else:
        msg = f'Extension is not supported: {file_extension}'
        raise NotImplementedError(msg)

    if os.path.exists(path):
        if overwrite:
            os.unlink(path)
        else:
            msg = f'File already exist. Use overwrite=True if needed: {path}'
            raise FileExistsError(msg)

    assert not os.path.exists(path), f'File still exists: {path}'
    os.rename(temp_file_path, path)


def _load(path):
    """Konkretus objektas i konkretu faila

    Jei filePath galune turi pletini '.gz', tai tariama, kad objektas buvo suarchyvuotas.
    Kitu atveju naudojamas tieisog pickle

    """

    file_path_name, file_extension = os.path.splitext(path)
    _, file_extension_deeper = os.path.splitext(file_path_name)

    if file_extension == '.gz':
        if file_extension_deeper == '.json':
            return Json.load(path=path)

        elif file_extension_deeper == '.jsonl':
            return Json.linesLoad(path=path)

        elif file_extension_deeper == '.csv':
            return pd.read_csv(path)

        elif file_extension_deeper == '.parquet':
            return pd.read_parquet(path)

        else:
            with gzip.open(path, 'rb') as fh:
                objDumps = fh.read()
            obj = pickle.loads(objDumps)
            return obj

    elif file_extension == '.bz2':
        if file_extension_deeper == '.json':
            return Json.load(path=path)

        elif file_extension_deeper == '.jsonl':
            return Json.linesLoad(path=path)

        else:
            with bz2.open(path, 'rb') as fh:
                objDumps = fh.read()
            obj = pickle.loads(objDumps)
            return obj

    elif file_extension == '.pkl':
        with open(path, "rb") as fh:
            obj = pickle.load(fh)
        return obj

    elif file_extension == '.parquet':
        return pd.read_parquet(path)

    elif file_extension == '.json':
        return Json.load(path=path)

    elif file_extension == '.jsonl':
        return Json.linesLoad(path=path)

    else:
        msg = f'Extension is not supported: {file_extension}'
        raise NotImplementedError(msg)


def load(path):
    try:
        return _load(path=path)
    except:
        msg = f'Failed to load object from: {path}'
        print(msg)
        raise


def dumps(obj):
    """Returns compressed obects string representation"""
    dumps = pickle.dumps(obj)
    cmp = gzip.compress(dumps)
    return cmp


def loads(cmp):
    """Returns obect from compressed representation created bu sumps"""
    dumps = gzip.decompress(cmp)
    obj = pickle.loads(dumps)
    return obj


def __dymmy__():
    import numpy as np
    import pandas as pd

    df = pd.DataFrame(np.random.randn(1000000, 5), columns=['a', 'b', 'c', 'd', 'e'])

    cmpstr = dumps(df)
    df2 = loads(cmpstr)
    df.equals(df2)

    obj = {'a': 4, "b": [1, 2, 3]}
    cmpstr = dumps(obj)
    obj2 = loads(cmpstr)
    print(obj == obj2)

    dump(df, 'temp.pkl')
    df2 = load('temp.pkl')
    df.equals(df2)

    dump(df, 'temp.pkl.gz')
    df2 = load('temp.pkl.gz')
    df.equals(df2)

    df.to_csv('temp.csv', index=False, sep=',')
    gzipFile('temp.csv', delSource=True)
    df2 = pd.read_csv('temp.csv.gz')
    df.equals(df2)
    (df - df2).abs().max().max()

    os.remove('temp.pkl')
    os.remove('temp.csv.gz')
    os.remove('temp.pkl.gz')
