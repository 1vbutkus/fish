__title__ = 'saveobj'
__version__ = '1.0.0'
__author__ = 'Vyganats Butkus'

from .saveobj import dump, dumps, gzipFile, load, loads

__all__ = [
    'dump',
    'load',
    'dumps',
    'loads',
    'gzipFile',
]
