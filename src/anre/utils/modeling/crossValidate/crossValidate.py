# mypy: disable-error-code="assignment,call-arg"
import pandas as pd
from sklearn.model_selection import GroupKFold, KFold

from anre.utils.modeling.diagnostic.metric import Metric
from anre.utils.modeling.model.leafModel.leafModel import LeafModel
from anre.utils.worker.worker import Worker


class CrossValidate:
    @classmethod
    def get_cvMeanDf(
        cls,
        model: LeafModel,
        xDf,
        ySr,
        cv: KFold | GroupKFold | int = 5,
        groups=None,
        worker=None,
        calcTrain=True,
    ) -> pd.DataFrame:
        cvCaseDf = cls.get_cvCaseDf(
            model=model, xDf=xDf, ySr=ySr, cv=cv, groups=groups, worker=worker, calcTrain=calcTrain
        )
        return cvCaseDf.mean().unstack(level=0)

    @classmethod
    def get_cvAggDf(
        cls,
        model: LeafModel,
        xDf,
        ySr,
        cv: KFold | GroupKFold | int = 5,
        groups=None,
        worker=None,
        calcTrain=True,
    ) -> pd.DataFrame:
        cvCaseDf = cls.get_cvCaseDf(
            model=model, xDf=xDf, ySr=ySr, cv=cv, groups=groups, worker=worker, calcTrain=calcTrain
        )
        return cvCaseDf.agg(['mean', 'std']).stack()

    @classmethod
    def get_cvCaseDf(
        cls,
        model: LeafModel,
        xDf,
        ySr,
        cv: KFold | GroupKFold | int = 5,
        groups=None,
        worker=None,
        calcTrain=True,
    ):
        if isinstance(cv, int):
            if groups is None:
                cv = KFold(n_splits=cv)
            else:
                cv = GroupKFold(n_splits=cv)

        worker = Worker.new_sequential(show_progress=True) if worker is None else worker

        assert isinstance(cv, (KFold, GroupKFold))
        cvSplit = cv.split(xDf, groups=groups)

        # trainIdx, testIdx = next(cvSplit):
        kwargsList = []
        for trainIdx, testIdx in cvSplit:
            kwargs = dict(model=model, xDf=xDf, ySr=ySr, trainIdx=trainIdx, testIdx=testIdx)
            kwargsList.append(kwargs)

        resList = worker.starmap(fun=cls._get_score, kwargs_list=kwargsList, calcTrain=calcTrain)
        resDf = pd.concat(resList, axis=1).transpose()
        # resDf = _resDf.agg(['mean', 'std', 'count']).stack()
        return resDf

    @classmethod
    def _get_score(
        cls, model: LeafModel, xDf: pd.DataFrame, ySr: pd.Series, trainIdx, testIdx, calcTrain
    ):
        assert not model.isFitted
        assert isinstance(xDf, pd.DataFrame)
        assert isinstance(ySr, pd.Series)
        model = model.copy()
        _xDf, _ySr = xDf.iloc[trainIdx], ySr.iloc[trainIdx]

        model.fit(_xDf, _ySr)

        resDict = {}

        if calcTrain:
            performanceSr = cls._get_performanceSr(model=model, xDf=_xDf, ySr=_ySr)
            resDict['train'] = performanceSr

        performanceSr = cls._get_performanceSr(
            model=model, xDf=xDf.iloc[testIdx], ySr=ySr.iloc[testIdx]
        )
        resDict['test'] = performanceSr

        resSr = pd.concat(resDict, axis=0)

        return resSr

    @staticmethod
    def _get_performanceSr(model, xDf, ySr) -> pd.Series:
        return Metric.get_targetPerformanceSr_fromModel(model=model, X=xDf, y=ySr)
