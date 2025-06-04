from typing import Any

from anre.type import Type
from anre.utils.modeling.model.hyperParameters.backend.iBackend import IBackend
from anre.utils.modeling.model.hyperParameters.backend.lgbm import Lgbm
from anre.utils.modeling.model.hyperParameters.hyperParameter import HyperParameter


class HpCatalog:
    @classmethod
    def new_lgbm(cls):
        return cls(backend=Lgbm())

    def __init__(self, backend: IBackend) -> None:
        assert isinstance(backend, IBackend)
        self._backend: IBackend = backend

    def get_hyperParameterList(self, **kwargs: Any) -> list[HyperParameter]:
        return self._backend.get_hyperParameterList()

    def get_hpKwargs(self, **kwargs: Any) -> dict[str, Type.BasicType]:
        return self.get_hpKwargs_fromHyperParameterList(
            hyperParameterList=self._backend.get_hyperParameterList(), **kwargs
        )

    @staticmethod
    def get_hpKwargs_fromHyperParameterList(
        hyperParameterList: list[HyperParameter], **kwargs
    ) -> dict[str, Type.BasicType]:
        hpKwargs = {hp.label: hp.value for hp in hyperParameterList}
        hpKwargs.update(**kwargs)
        return hpKwargs
