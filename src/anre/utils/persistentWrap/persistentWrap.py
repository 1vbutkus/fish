# mypy: disable-error-code="valid-type,var-annotated"
import os
from typing import Any, Callable

from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.persistentWrap.default import missing
from anre.utils.persistentWrap.wrapper import Wrapper
from anre.utils.safeWrap.failedObj import FailedObj
from anre.utils.safeWrap.safeWrap import SafeWrap
from anre.utils.worker.worker import Worker


class PersistentWrap:
    @classmethod
    def decorator(
        cls,
        fun=None,
        *,
        file_template: str | None = None,
        cache_dir_path: str | None = None,
        skip_args: list | None = None,
        default_use_cache: int = 1,
        default_check_prob: float = 0,
        default_verbose: bool = False,
    ) -> Callable[[Callable], Wrapper]:
        assert fun is None, (
            'Please use PersistentWrap.decorator() instead of @PersistentWrap.decorator'
        )

        if cache_dir_path is None:
            cache_dir_path = FileSystem.create_os_cache_dir(cls.__name__, 'individual')
        if file_template is None:
            file_template = os.path.join("{cls}", "{fun}", "cache_{hash}.pkl")

        wrapper = Wrapper(
            file_template=file_template,
            cache_dir_path=cache_dir_path,
            skip_args=skip_args,
            default_use_cache=default_use_cache,
            default_check_prob=default_check_prob,
            default_verbose=default_verbose,
        )
        return wrapper.assign_fun

    @classmethod
    def get_fun_res_exist_list(
        cls,
        fun: Callable,
        kwargs_list: list[{str: Any}],
        cache_dir_path: str | None = None,
        skip_args: list | None = None,
        **kwargs,
    ) -> list[Any]:
        # collect fun and wrap arguments to pass
        run_fun, safe_kwargs, wrap_kwargs = cls._get_fun_and_wrap_args(
            fun=fun,
            cache_dir_path=cache_dir_path,
            skip_args=skip_args,
            reset_cache=False,
            verbose=False,
        )

        # get full kwargs
        full_kwargs_list = cls._get_updated_kwargs_list(kwargs_list=kwargs_list, **kwargs)

        _fn_cached = cls._cache_fun(fun=run_fun, safe_kwargs=safe_kwargs, wrap_kwargs=wrap_kwargs)
        assert isinstance(_fn_cached, Wrapper)

        exist_list = [_fn_cached.get_is_file_exist(**kwargs) for kwargs in full_kwargs_list]
        return exist_list

    @classmethod
    def get_fun_res_list(
        cls,
        fun: Callable,
        kwargs_list: list[{str: Any}],
        cache_dir_path: str | None = None,
        skip_args: list | None = None,
        reset_cache=False,
        use_cache: int = 1,
        worker: Worker | None = None,
        obj_if_failed: Any = FailedObj(),
        rerun_if_failed=False,
        verbose=False,
        **kwargs,
    ) -> list[Any]:
        if worker is None:
            # Note that loading from pickles uses C implementation and thus can benefit from
            # threading backend of joblib, use prefer='threads'
            # But this is efficient only if you do not need to actually calculate values. In this case we want to be real parallel
            worker = Worker.new_joblib(show_progress=True, prefer=None)

        # collect fun and wrap arguments to pass
        run_fun, safe_kwargs, wrap_kwargs = cls._get_fun_and_wrap_args(
            fun=fun,
            cache_dir_path=cache_dir_path,
            skip_args=skip_args,
            reset_cache=reset_cache,
            verbose=verbose,
        )

        # get full kwargs
        full_kwargs_list = cls._get_updated_kwargs_list(kwargs_list=kwargs_list, **kwargs)

        # make a sorted dict for kwargs, so that we can update from mixture
        kwList = list(range(len(kwargs_list)))
        kwargsDict = {kwi: kwargs for kwi, kwargs in zip(kwList, full_kwargs_list)}

        if use_cache > 0:
            ### try to load objects that exist
            _fn_cached = cls._cache_fun(
                fun=run_fun, safe_kwargs=safe_kwargs, wrap_kwargs=wrap_kwargs
            )
            wrappedResultDict_good = {
                kwi: _fn_cached.load_if_not_missing(_returnIfMissing=missing, **kwargs)
                for kwi, kwargs in kwargsDict.items()
            }
            wrappedResultDict_good = {
                kwi: wrappedResult
                for kwi, wrappedResult in wrappedResultDict_good.items()
                if wrappedResult is not missing
            }
            if rerun_if_failed and safe_kwargs is not None:
                wrappedResultDict_good = {
                    kwi: wrappedResult
                    for kwi, wrappedResult in wrappedResultDict_good.items()
                    if wrappedResult.success
                }
            kwargsDict_toRun = {
                kwi: kwargs
                for kwi, kwargs in kwargsDict.items()
                if kwi not in wrappedResultDict_good
            }

        else:
            wrappedResultDict_good = {}
            kwargsDict_toRun = kwargsDict

        ### run function in parallel
        if kwargsDict_toRun:
            kwi_toRun = list(kwargsDict_toRun.keys())
            _kwargsList_toRun = [
                dict(
                    fun=run_fun,
                    fun_kwargs=kwargsDict_toRun[kwi],
                    safe_kwargs=safe_kwargs,
                    wrap_kwargs=wrap_kwargs,
                )
                for kwi in kwi_toRun
            ]
            _wrappedResultList = worker.starmap(
                cls._wrap_and_execute,
                kwargs_list=_kwargsList_toRun,
            )
            wrappedResultDict_new = {
                kwi: wrappedResult for kwi, wrappedResult in zip(kwi_toRun, _wrappedResultList)
            }
        else:
            wrappedResultDict_new = {}

        # merge and collect results to be in order
        assert not set(wrappedResultDict_good) & set(wrappedResultDict_new)
        _wrappedResultDict = {**wrappedResultDict_good, **wrappedResultDict_new}
        wrappedResultList = [_wrappedResultDict[kwi] for kwi in kwList]
        if safe_kwargs is None:
            resultsList = wrappedResultList
        else:
            resultsList = SafeWrap.get_resultsList(
                wrappedResultList=wrappedResultList, objIfFailed=obj_if_failed, verbose=verbose
            )

        return resultsList

    @staticmethod
    def _get_updated_kwargs_list(kwargs_list: list[dict], **kwargs: Any):
        assert isinstance(kwargs_list, list)
        _kwargsList = []
        for kwargs_i in kwargs_list:
            kwargs_i = kwargs_i.copy()
            assert not (set(kwargs_i) & set(kwargs)), (
                f'Arguments overlap: {set(kwargs_i) & set(kwargs)}'
            )
            kwargs_i.update(kwargs)
            _kwargsList.append(kwargs_i)
        return _kwargsList

    @classmethod
    def _get_fun_and_wrap_args(
        cls,
        fun: Callable,
        cache_dir_path: str | None,
        skip_args: list | None,
        reset_cache: bool,
        verbose: bool,
    ):
        if isinstance(fun, Wrapper):
            run_fun = fun.fun
            wrap_kwargs = fun.get_kwargs()
            assert cache_dir_path is None
            assert skip_args is None
            assert reset_cache is False
            safe_kwargs = None

        else:
            run_fun = fun
            assert cache_dir_path is not None
            funCacheDirPath = os.path.join(cache_dir_path, cls.__name__, 'atScale', fun.__name__)
            FileSystem.create_folder(funCacheDirPath, recreate=reset_cache)
            wrap_kwargs = dict(
                file_template='case_{hash}.pkl',
                cache_dir_path=funCacheDirPath,
                skip_args=skip_args,
                default_use_cache=1,
                default_check_prob=0,
                default_verbose=verbose,
            )
            safe_kwargs = dict()

        return run_fun, safe_kwargs, wrap_kwargs

    @staticmethod
    def _cache_fun(fun: Callable, safe_kwargs: dict | None = None, wrap_kwargs: dict | None = None):
        run_fun = fun

        if safe_kwargs is not None:
            run_fun = SafeWrap.decorator(**safe_kwargs)(run_fun)

        if wrap_kwargs is not None:
            run_fun = Wrapper(**wrap_kwargs).assign_fun(run_fun)

        return run_fun

    @classmethod
    def _wrap_and_execute(
        cls,
        fun: Callable,
        fun_kwargs: dict | None = None,
        safe_kwargs: dict | None = None,
        wrap_kwargs: dict | None = None,
    ):
        run_fun = cls._cache_fun(fun=fun, safe_kwargs=safe_kwargs, wrap_kwargs=wrap_kwargs)
        res = run_fun(**fun_kwargs, _use_cache=0)
        return res
