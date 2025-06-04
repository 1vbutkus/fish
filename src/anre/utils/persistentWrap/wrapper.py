# mypy: disable-error-code="assignment"
import inspect
import os
import random
import warnings
from functools import update_wrapper
from typing import Any, Callable

from anre.utils import saveobj
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.hash.hash import Hash
from anre.utils.persistentWrap.default import NoDefault, noDefault


class Wrapper:
    break_change_version: int = 0

    def __init__(
        self,
        file_template: str,
        cache_dir_path: str,
        skip_args: list | None,
        default_use_cache: int,
        default_check_prob: float,
        default_verbose: bool,
        **kwargs,
    ):
        assert isinstance(cache_dir_path, str)
        assert isinstance(file_template, str)
        assert isinstance(skip_args, list) or skip_args is None
        assert isinstance(default_use_cache, int)
        assert isinstance(default_check_prob, (int, float))
        assert 0 <= default_check_prob <= 1
        assert isinstance(default_verbose, bool)

        self._fun = None
        self._signature = None
        self._firstArgName: str | None = None

        self._file_template = file_template
        self._cache_dir_path = cache_dir_path
        self._skip_args = skip_args
        self._default_use_cache = default_use_cache
        self._default_check_prob = default_check_prob
        self._default_verbose = default_verbose
        self._save_kwargs = kwargs

    def __call__(
        self, *args, _use_cache=noDefault, _check_prob=noDefault, _verbose=noDefault, **kwargs
    ):
        _use_cache = self._default_use_cache if _use_cache is noDefault else _use_cache
        _check_prob = self._default_check_prob if _check_prob is noDefault else _check_prob
        _verbose = self._default_verbose if _verbose is noDefault else _verbose

        if _use_cache < 0:
            if _verbose:
                print('Cash is not used, since _use_cache < 0.')
            return self._fun(*args, **kwargs)

        bound_arguments = self._get_bound_arguments(*args, **kwargs)
        file_path = self._get_file_path(bound_arguments=bound_arguments)
        if _use_cache > 0:
            isDataFromCache, resFromCache = self._load_obj_if_not_missing_from_path(
                file_path=file_path
            )
        else:
            isDataFromCache, resFromCache = False, None

        ### if we have what to return, we randomly decide to return, o to crosscheck
        if isDataFromCache:
            if _check_prob == 0 or random.uniform(a=1e-7, b=1) > _check_prob:
                if _verbose:
                    print('Object returned from cache (no checking):', file_path)
                return resFromCache
            else:
                if _verbose:
                    print(
                        'We have an object in cache, but we will rerun the function to make sure it matches.'
                    )

        ### actual run
        res = self._fun(*bound_arguments.args, **bound_arguments.kwargs)
        # if we have the value, lets compare the hash.
        if isDataFromCache:
            assert Hash.get_hash(obj=res) == Hash.get_hash(obj=resFromCache), (
                f'The hash from file and runtime results are not matching. Please run {self._fun.__name__}(*{bound_arguments.args}, **{bound_arguments.kwargs}, _checkProb=1)'
            )
            if _verbose:
                print('We have cross checked data in cache and runtime. Status: OK')

        # make sure we have the folder to save
        dirPath = os.path.dirname(file_path)
        if not os.path.exists(dirPath):
            if _verbose:
                print("Creating cache dir:", dirPath)
            FileSystem.create_folder(dirPath)

        saveobj.dump(obj=res, path=file_path, overwrite=True, **self._save_kwargs)
        if _verbose:
            print('The results are saved in:', file_path)

        return res

    @property
    def fun(self) -> Callable:
        assert self._fun is not None
        return self._fun

    def assign_fun(self, fun: Callable):
        self._fun = fun
        self._signature = inspect.signature(fun)
        assert self._signature is not None
        self._firstArgName = (
            list(self._signature.parameters)[0] if self._signature.parameters else None
        )
        update_wrapper(self, self._fun)
        return self

    def load_if_not_missing(
        self, *args, _returnIfMissing: NoDefault | Any = noDefault, **kwargs: Any
    ):
        bound_arguments = self._get_bound_arguments(*args, **kwargs)
        file_path = self._get_file_path(bound_arguments=bound_arguments)
        is_data, obj = self._load_obj_if_not_missing_from_path(file_path=file_path)
        if is_data:
            return obj
        else:
            return _returnIfMissing

    def get_is_file_exist(self, *args: Any, **kwargs: Any) -> bool:
        bound_arguments = self._get_bound_arguments(*args, **kwargs)
        file_path = self._get_file_path(bound_arguments=bound_arguments)
        return os.path.exists(file_path)

    def get_kwargs(self) -> dict:
        return dict(
            file_template=self._file_template,
            cache_dir_path=self._cache_dir_path,
            skip_args=self._skip_args,
            default_use_cache=self._default_use_cache,
            default_check_prob=self._default_check_prob,
            default_verbose=self._default_verbose,
        )

    ##################################################################################################################################

    def _get_bound_arguments(self, *args: Any, **kwargs: Any) -> inspect.BoundArguments:
        assert self._signature is not None
        try:
            bound_arguments = self._signature.bind(*args, **kwargs)
        except TypeError:
            raise AssertionError(
                'Call of function missmatch signature or PersistentCash function was used on instance functions.'
            )
        bound_arguments.apply_defaults()
        return bound_arguments

    def _get_file_path(self, bound_arguments: inspect.BoundArguments) -> str:
        className = '__noClass__'
        inputArgDict = bound_arguments.arguments.copy()
        if inputArgDict:
            assert isinstance(self._firstArgName, str)
            firstArg = inputArgDict[self._firstArgName]
            assert self._fun is not None
            if self._firstArgName in ['self', 'cls'] and hasattr(firstArg, self._fun.__name__):
                # this is a class or an instance
                if inspect.isclass(firstArg):
                    className = firstArg.__name__
                    del inputArgDict[self._firstArgName]
                else:
                    raise AssertionError(
                        'Persistent Has function should not be called on instance functions.'
                    )

        if self._skip_args:
            assert set(self._skip_args) <= set(inputArgDict), (
                f'skip_args={self._skip_args} not in inputArgDict={inputArgDict}'
            )
            for arg_name in self._skip_args:
                del inputArgDict[arg_name]

        hashValue = Hash.get_dictHash(inputArgDict)
        hashValue += f'_v{self.break_change_version}'

        assert self._fun is not None
        funModuleName = self._fun.__module__ if hasattr(self._fun, '__module__') else '__noModule__'
        _fileRelPath = self._file_template.format(
            module=funModuleName,
            cls=className,
            fun=self._fun.__name__,
            hash=hashValue,
            **inputArgDict,
        )
        file_path = os.path.join(self._cache_dir_path, _fileRelPath)
        return file_path

    def _load_obj_if_not_missing_from_path(self, file_path: str) -> tuple[bool, Any]:
        ### try to load
        is_data = False
        obj = None
        if os.path.exists(file_path):
            try:
                obj = saveobj.load(path=file_path)
                is_data = True
            except BaseException:
                msg = f'Failed to load object from pkl file. Recalculation will be run. cache File: {file_path}'
                warnings.warn(msg)

        return is_data, obj
