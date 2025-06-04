import pandas as pd

from anre.utils.timeSeries.smooth.exponentialMovingAverage.exponentialMovingAverage import (
    ExponentialMovingAverage,
)


class ConstantMotionTransformation:
    @staticmethod
    def validate_constantMotion(
        motionDf: pd.DataFrame, stepSize: float | int | None = None
    ) -> bool:
        if motionDf.empty:
            return True
        assert isinstance(motionDf, pd.DataFrame)
        assert motionDf.index.is_monotonic_increasing
        assert motionDf.index.is_unique
        assert not motionDf.index.isna().any()
        diffSr = motionDf.index.to_series().diff()
        if (~diffSr.isna()).any():
            if stepSize is None:
                stepSize = diffSr.median()
            maxDeiationFormTimeGrid = (diffSr.fillna(stepSize) - stepSize).abs().max()
            assert maxDeiationFormTimeGrid < 1e-4, (
                f'On on time grid: {maxDeiationFormTimeGrid=}, {stepSize=}'
            )
        return True

    @classmethod
    def get_emaDf(
        cls, motionDf: pd.DataFrame, transFields: list[str], halflifes: list[float | int]
    ) -> pd.DataFrame:
        cls.validate_constantMotion(motionDf=motionDf)
        assert transFields
        assert halflifes
        assert set(transFields) <= set(motionDf.columns), (
            f'Fields {set(transFields) - set(motionDf.columns)} not in columns.'
        )

        srDict = {}
        ### exponentialMovingAverage
        tdf = motionDf[transFields]
        for field in transFields:
            for halflife in halflifes:
                label = f'{field}_ema{halflife}'
                sr = ExponentialMovingAverage.get_emaSr_fromSr(sr=tdf[field], halflife=halflife)
                sr.index = motionDf.index
                srDict[label] = sr

        resDf = pd.concat(srDict, axis=1)
        assert resDf.index.equals(motionDf.index)

        return resDf

    @classmethod
    def get_rollExtDf(
        cls,
        motionDf: pd.DataFrame,
        transFields: list[str],
        wins: list[float | int],
        funs=('min', 'max'),
    ) -> pd.DataFrame:
        cls.validate_constantMotion(motionDf=motionDf)
        assert transFields
        assert wins
        assert funs
        assert set(funs) <= {'min', 'max'}
        assert set(transFields) <= set(motionDf.columns), (
            f'Fields {set(transFields) - set(motionDf.columns)} not in columns.'
        )

        srDict = {}
        ### rolling (min, max)
        for field in transFields:
            sr = motionDf[field]
            for win in wins:
                if 'min' in funs:
                    srDict[f'{field}_rolMin{win}'] = sr.rolling(win).min()  # type: ignore[arg-type]
                if 'max' in funs:
                    srDict[f'{field}_rolMax{win}'] = sr.rolling(win).max()  # type: ignore[arg-type]

        resDf = pd.concat(srDict, axis=1)
        assert resDf.index.equals(motionDf.index)

        return resDf

    @classmethod
    def get_rollMedianExtDf(
        cls,
        motionDf: pd.DataFrame,
        transFields: list[str],
        medWins: list[float | int],
        extWins: list[float | int],
        funs=('min', 'max'),
    ) -> pd.DataFrame:
        cls.validate_constantMotion(motionDf=motionDf)
        assert transFields
        assert medWins
        assert extWins
        assert funs
        assert set(funs) <= {'min', 'max'}
        assert set(transFields) <= set(motionDf.columns), (
            f'Fields {set(transFields) - set(motionDf.columns)} not in columns.'
        )

        srDict = {}

        ### rolling median-Min/Max
        for field in transFields:
            sr = motionDf[field]
            for medWin in medWins:
                for extWin in extWins:
                    if 'min' in funs:
                        srDict[f'{field}_rolMedian{medWin}_rolMin{extWin}'] = (
                            sr.rolling(medWin, min_periods=int(medWin / 2))  # type: ignore[arg-type]
                            .median()
                            .rolling(extWin, min_periods=int(extWin / 2))  # type: ignore[arg-type]
                            .min()
                        )
                    if 'max' in funs:
                        srDict[f'{field}_rolMedian{medWin}_rolMax{extWin}'] = (
                            sr.rolling(medWin, min_periods=int(medWin / 2))  # type: ignore[arg-type]
                            .median()
                            .rolling(extWin, min_periods=int(extWin / 2))  # type: ignore[arg-type]
                            .max()
                        )

        resDf = pd.concat(srDict, axis=1)
        assert resDf.index.equals(motionDf.index)

        return resDf
