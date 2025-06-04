# mypy: disable-error-code="assignment,override,syntax,var-annotated"
from __future__ import annotations

import copy
import logging
import os
from typing import Iterable

import dict_deep
import pandas as pd

from anre.utils.dotNest.dotNest import DotNest
from anre.utils.hash.hash import Hash
from anre.utils.Json.Json import Json
from anre.utils.prettyprint.prettyprint import PrettyPrint
from anre.utils.yaml_.yaml import Yaml

logger = logging.getLogger(__name__)


class Parameter:
    def __init__(
        self, *params, pathToPredefined: str | list[str] | None = None, skipValidation=False
    ):
        predefinedDict = self._get_predefinedDict(pathToPredefined=pathToPredefined)  # type: ignore[arg-type]
        paramDotDicts = self._paramsToParamsDotDicts(*params, predefinedDict=predefinedDict)
        paramDotDict = self._combineParamDotDicts(*paramDotDicts)
        paramDotDict = self._sortParamsDotDict(paramDotDict=paramDotDict)
        paramDerivedDotDict = self._calculateParamsDerivedDotDict(paramDotDict=paramDotDict)

        if not skipValidation:
            assert self._validate(
                paramDotDict=paramDotDict, paramDerivedDotDict=paramDerivedDotDict
            )
        self._paramDotDict = paramDotDict
        self._paramDerivedDotDict = paramDerivedDotDict

        self._pathToPredefined = pathToPredefined

    ### functions to override:

    @classmethod
    def _beforeParamsFoldFun(cls, paramDotDict: dict, resultDotDict: dict) -> (dict, dict):
        return paramDotDict, resultDotDict

    @classmethod
    def _paramsDerivedDotDictFun(cls, paramDotDict) -> dict:
        return {}

    @classmethod
    def _validate(cls, paramDotDict, paramDerivedDotDict) -> bool:
        return True

    ###################################################################################################################

    def __repr__(self) -> str:
        resStr = f'{self.__class__.__name__}:\n'
        if self.paramDerivedDict:
            resStr += (
                f' - derived:\n{PrettyPrint.get_dictStr(obj=self.paramDerivedDict, indent=2)}\n'
            )
            resStr += f' - base:\n{PrettyPrint.get_dictStr(obj=self.paramDict, indent=2)}'
        else:
            resStr += PrettyPrint.get_dictStr(obj=self.paramDict, indent=2)
        return resStr

    def __getitem__(self, key: str):
        assert type(key) is str, f'Parameters getter not implement for type {type(key)}'

        allParamsDotDict = {**self.paramDotDict, **self.paramDerivedDotDict}

        # We do not include derived parameters when searching for a matching base by design. Derived parameters
        # should not be returned when returning nested dicts from this method because nested dicts should only be used
        # for transplanting parameter branches only. Setting derived parameters directly is not allowed, so including
        # them in the nested dicts would violate this as the nested dicts should only be used for setting parameters.
        shorterKeys, longerKeys = self._findKeysWithCommonBase(key, self.paramDotDict)
        if not any([shorterKeys, longerKeys, key in allParamsDotDict]):
            raise KeyError(f'no keys in Parameters with base {key}\n{self}')

        if key in allParamsDotDict:
            return allParamsDotDict[key]
        else:
            return dict_deep.deep_get(self.paramDict, key.split('.'))

    def __eq__(self, other: Parameter) -> bool:
        return self.hash() == other.hash()

    def get(self, key: str, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def set(self, *params, pathToPredefined: str | None = None, skipValidation: bool = False):
        pathToPredefined = pathToPredefined if pathToPredefined else self._pathToPredefined
        return self.__class__(
            self.paramDotDict,
            *params,
            pathToPredefined=pathToPredefined,
            skipValidation=skipValidation,
        )

    def drop(self, dotKey: str, raiseIfMissing: bool = True, skipValidation: bool = False):
        paramsDictCopy = self.paramDict.copy()
        DotNest.nestDel(paramsDictCopy, dotKey, raiseIfMissing=raiseIfMissing)
        return self.__class__(
            paramsDictCopy, pathToPredefined=self._pathToPredefined, skipValidation=skipValidation
        )

    @property
    def paramDotDict(self) -> dict:
        return copy.deepcopy(self._paramDotDict)

    @property
    def paramDerivedDotDict(self) -> dict:
        return copy.deepcopy(self._paramDerivedDotDict)

    @property
    def paramDict(self) -> dict:
        return self._dotDictToDict(self.paramDotDict)

    @property
    def paramDerivedDict(self) -> dict:
        return self._dotDictToDict(self.paramDerivedDotDict)

    def hash(self) -> str:
        return Hash.get_dictHash(self.paramDotDict)

    @classmethod
    def _get_predefinedDict(cls, pathToPredefined: str | list[str]) -> dict:
        if pathToPredefined is None:
            return {}

        elif isinstance(pathToPredefined, list):
            predefinedDictList = [
                cls._get_predefinedDict_single(pathToPredefined=singlePathToPredefined)
                for singlePathToPredefined in pathToPredefined
            ]
            predefinedDict = {k: v for d in predefinedDictList for k, v in d.items()}
            return predefinedDict

        else:
            return cls._get_predefinedDict_single(pathToPredefined=pathToPredefined)

    @classmethod
    def _get_predefinedDict_single(cls, pathToPredefined: str) -> dict:
        if pathToPredefined is not None:
            filename, file_extension = os.path.splitext(pathToPredefined)
            if file_extension == '.yaml':
                resDict = Yaml.load(pathToPredefined, cache=True)
            elif file_extension == '.json':
                resDict = Json.load(pathToPredefined, cache=True)
            else:
                msg = f'Unsupported file extension provided to pathToPredefined in Parameter: {file_extension}'
                raise NotImplementedError(msg)
        else:
            return {}

        if resDict is None:
            resDict = {}

        return resDict

    @classmethod
    def _paramsToParamsDotDicts(cls, *params, predefinedDict: dict):
        def flattenToList(x, acc: list | None = None):
            acc = acc if acc else []
            if isinstance(x, Iterable) and not isinstance(x, dict) and not isinstance(x, str):
                for xi in x:
                    acc += flattenToList(xi)
            else:
                acc += [x]
            return acc

        def tryConvertToDict(prm):
            if isinstance(prm, str):
                if prm not in predefinedDict:
                    raise KeyError(f"Label `{prm}` not found in predefined parameter set")
                return predefinedDict[prm]
            elif isinstance(prm, Parameter):
                return prm.paramDotDict
            else:
                return prm

        def dictToDotDict(prm):
            def flattenDictToDotDict(
                someDict: dict, dotDictAcc: dict | None = None, keyBase: str = ''
            ):
                dotDictAcc = dotDictAcc if dotDictAcc else {}
                for key, value in someDict.items():
                    newKeyBase = key if keyBase == '' else f'{keyBase}.{key}'
                    if type(value) is dict and len(value) > 0:
                        dotDictAcc = flattenDictToDotDict(value, dotDictAcc, newKeyBase)
                    else:
                        dotDictAcc[newKeyBase] = value  # type: ignore[index]
                return dotDictAcc

            if isinstance(prm, dict):
                dotDict = flattenDictToDotDict(prm)
                for key, value in dotDict.items():
                    shorterKeys, longerKeys = cls._findKeysWithCommonBase(key, dotDict)
                    assert not (keys := shorterKeys + longerKeys), (
                        f'Building dotDict failed: key {key} overlaps with keys {keys}'
                    )
                return dotDict
            else:
                raise NotImplementedError(f"Unexpected parameter type: {type(prm)}, {prm}")

        def convertAndFlattenFun(xs):
            return flattenToList(map(tryConvertToDict, flattenToList(xs)))

        flatList = convertAndFlattenFun(params)
        while convertAndFlattenFun(flatList) != flatList:
            flatList = convertAndFlattenFun(flatList)

        return [dictToDotDict(x) for x in flatList]

    def diff(
        self,
        other: Parameter,
        selfName='self',
        otherName='other',
        withDerived=True,
        ignoreList: list[str] | None = None,
    ) -> pd.DataFrame:
        ignoreList = ignoreList if ignoreList else []
        selfParamsDotDict = (
            {**self.paramDotDict, **self.paramDerivedDotDict} if withDerived else self.paramDotDict
        )
        otherParamsDotDict = (
            {**other.paramDotDict, **other.paramDerivedDotDict}
            if withDerived
            else other.paramDotDict
        )
        selfSr = pd.Series(selfParamsDotDict).drop(labels=ignoreList, errors='ignore').sort_index()
        otherSr = (
            pd.Series(otherParamsDotDict).drop(labels=ignoreList, errors='ignore').sort_index()
        )
        eqSer = selfSr.eq(otherSr)
        diffSer = eqSer[~eqSer]
        derivedSr = diffSer.index.map(
            lambda x: x in {**self.paramDerivedDotDict, **other.paramDerivedDotDict}
        )
        res = pd.DataFrame(
            list(
                zip(
                    diffSer.index,
                    derivedSr,
                    selfSr.reindex(diffSer.index),
                    otherSr.reindex(diffSer.index),
                )
            ),
            columns=['parameter', 'derived', selfName, otherName],
        )
        res.set_index('parameter', inplace=True)
        return res

    @classmethod
    def _combineParamDotDicts(cls, *paramDotDicts: dict) -> dict:
        resultDotDict = {}
        for paramsDotDict in paramDotDicts:
            paramsDotDict, resultDotDict = cls._beforeParamsFoldFun(paramsDotDict, resultDotDict)
            for key, value in paramsDotDict.items():
                shorterKeys, longerKeys = cls._findKeysWithCommonBase(key, resultDotDict)

                shorterKeysToRemove = [x for x in shorterKeys if key.startswith(f'{x}.')]
                longerKeysToRemove = [x for x in longerKeys if x.startswith(f'{key}.')]

                for keyToRemove in shorterKeysToRemove + longerKeysToRemove:
                    logger.debug(f'removing parameter {keyToRemove} = {resultDotDict[keyToRemove]}')
                    resultDotDict.pop(keyToRemove)

                if key in resultDotDict and (rddValue := resultDotDict[key]) != value:
                    logger.debug(f'overriding parameter {key}: {rddValue} -> {value}')

                resultDotDict[key] = value
        return resultDotDict

    @classmethod
    def _sortParamsDotDict(cls, paramDotDict: dict):
        return dict(sorted(paramDotDict.items(), key=lambda x: x[0]))

    @classmethod
    def _calculateParamsDerivedDotDict(cls, paramDotDict: dict) -> dict:
        derivedDotDict = cls._paramsDerivedDotDictFun(paramDotDict)
        conflictingKeys = list(set(derivedDotDict.keys()).intersection(set(paramDotDict.keys())))
        assert not conflictingKeys, (
            f'paramsDerivedDotDictFun tried to overwrite keys that are already present in Parameters: {conflictingKeys}'
        )
        return derivedDotDict

    @classmethod
    def _findKeysWithCommonBase(cls, key: str, dotDict: dict) -> (list, list):
        keyLength = key.count('.')
        shorterKeys = [x for x in dotDict.keys() if x.count('.') < keyLength]
        longerKeys = [x for x in dotDict.keys() if x.count('.') > keyLength]
        shorterKeysWithCommonBase = [x for x in shorterKeys if key.startswith(f'{x}.')]
        longerKeysWithCommonBase = [x for x in longerKeys if x.startswith(f'{key}.')]
        return shorterKeysWithCommonBase, longerKeysWithCommonBase

    @classmethod
    def _dotDictToDict(cls, dotDict: dict) -> dict:
        resultDict = {}
        for key, value in dotDict.items():
            intermediateDict = resultDict
            for i, keyPart in enumerate(keys := key.split('.'), start=1):
                if keyPart not in intermediateDict and i < len(keys):
                    intermediateDict[keyPart] = {}
                if i == len(keys):
                    intermediateDict[keyPart] = value  # if value is not None else {}
                intermediateDict = intermediateDict[keyPart]

        return resultDict
