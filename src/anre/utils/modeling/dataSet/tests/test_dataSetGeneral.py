# mypy: disable-error-code="union-attr"
import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.modeling.dataSet.dataSetGeneral import DataSetGeneral


class TestDataSet(testutil.TestCase):
    def test_new_constructors_happyPath(self) -> None:
        XAr = np.random.rand(10, 3)
        yAr = np.random.rand(10)

        dsList = [
            DataSetGeneral.new(X=XAr, y=yAr),
            DataSetGeneral.new(X=pd.DataFrame(XAr, columns=["X0", "X1", "X2"]), y=yAr),
            DataSetGeneral.new(X=pd.DataFrame(XAr, columns=["X0", "X1", "X2"]), y=pd.Series(yAr)),
            DataSetGeneral.new(X=XAr, y=pd.Series(yAr)),
        ]
        ds = dsList[0]
        assert ds.equals(ds)
        self.assertTrue(all([ds.equals(_ds) for _ds in dsList]))

    def test_flat_happyPath(self) -> None:
        df = pd.DataFrame(np.random.rand(10, 5), columns=list("ABCDE"))
        df["groups"] = pd.Series(np.array([0, 1] * 5))
        headerDict = {"X": ["A", "B"], "y": "E", "groups": "groups"}
        ds = DataSetGeneral(df=df, name="testName", headerDict=headerDict)  # type: ignore[arg-type]

        assert ds.X.equals(df[["A", "B"]])
        assert ds.y.equals(df["E"])

        extraSr = pd.Series(np.random.rand(10))
        ds["extray"] = extraSr
        assert ds.extray.equals(extraSr)

        extraDf = pd.DataFrame(np.random.rand(10, 2), columns=list("ab"))
        ds["extraX"] = extraDf
        assert ds.extraX.equals(extraDf)

        # repeat assigment
        ds["extraX"] = extraDf
        assert ds.extraX.equals(extraDf)

        ds2 = ds.copy()
        assert ds2.equals(ds)

        AAA = pd.Series(np.random.rand(10))
        BBB = pd.Series(np.random.rand(10))
        ds3 = ds.set(AAA=AAA, BBB=BBB)
        assert "AAA" in ds3
        assert "AAA" not in ds
        assert ds3.X.equals(df[["A", "B"]])
        assert ds3.y.equals(df["E"])
        assert ds3.AAA.equals(AAA)
        assert ds3.BBB.equals(BBB)

        ### assign and reassign
        ds["y"] = "A"
        assert ds.y.equals(df["A"])
        ds["y"] = ds.df["A"]
        assert ds.y.equals(df["A"])
        ds["X"] = ["C", "D"]
        assert ds.X.equals(df[["C", "D"]])

        ds["y"] = ds.df["B"] * 2
        assert ds.y.equals(df["B"] * 2)

        ds["X"] = df[["C", "D"]] * 2
        assert ds.X.equals(df[["C", "D"]] * 2)

    def test_groups(self) -> None:
        X = np.random.rand(10, 3)
        y = np.random.rand(10)
        groups = pd.Series(np.array([0, 1] * 5))

        aDs = DataSetGeneral.new(X=X, y=y, groups=groups, name="ds1")
        bDs = DataSetGeneral.new(X=X, y=y, name="ds2")

        assert aDs.groups.equals(groups)
        assert bDs.groups is None

    def test_accessAndManipulation(self) -> None:
        XDf = pd.DataFrame(np.random.rand(10, 5), columns=list("ABCDE"))
        extraDf = pd.DataFrame(np.random.rand(10, 2), columns=list("XY"))
        groups = pd.Series([1, 2] * 5)
        ySr = pd.Series(np.random.rand(10), name="yName")

        ds = DataSetGeneral.new(X=XDf, y=ySr, groups=groups, extra=extraDf)

        assert ds.X.equals(XDf)
        assert ds["X"].equals(XDf)
        assert ds.y.equals(ySr)
        assert ds["y"].equals(ySr)
        assert ds.groups.equals(groups)
        assert ds["groups"].equals(groups)
        assert ds.extra.equals(extraDf)
        assert ds["extra"].equals(extraDf)

        ind = ds["y"] > 0.5
        assert isinstance(ds.loc[ind], DataSetGeneral)
        assert isinstance(ds.iloc[[1, 2]], DataSetGeneral)

        with self.assertRaises(AssertionError):
            _ = ds.iloc[1]

        assert "extra" in ds
        assert "extra" in ds.keys()
        assert "extra" not in ds.drop_header(header="extra").keys()
        assert "extra" not in ds
        assert {"X", "Y"} <= set(ds.df.columns)

        extraSr2 = pd.Series(np.random.rand(10))
        ds["extray"] = extraSr2
        assert ds.extray.equals(extraSr2)

        extraDf2 = pd.DataFrame(np.random.rand(10, 2), columns=list("ab"))
        ds["extraX"] = extraDf2
        assert ds.extraX.equals(extraDf2)

        ds2 = ds.copy()
        assert ds2.equals(ds)

        AAA = pd.Series(np.random.rand(10))
        BBB = pd.Series(np.random.rand(10))
        ds3 = ds.set(AAA=AAA, BBB=BBB)
        assert ds3.X.equals(XDf)
        assert ds3.y.equals(ySr)
        assert ds3.AAA.equals(AAA)
        assert ds3.BBB.equals(BBB)

    def test_concat_noGroups(self) -> None:
        X = np.random.rand(10, 3)
        y = np.random.rand(10)

        aDs = DataSetGeneral.new(X=X, y=y, name="ds1")
        bDs = DataSetGeneral.new(X=X, y=y, name="ds2")
        dsList = [aDs, bDs]
        ds1 = DataSetGeneral.concat(dsList=dsList)
        ds2 = DataSetGeneral.concat(dsList=dsList, creatNewGroupsFromNames=True)

        assert ds1.groups is None
        assert isinstance(ds2.groups, pd.Series)

    def test_concat_withGroups(self) -> None:
        X = np.random.rand(10, 3)
        y = np.random.rand(10)
        groups = pd.Series(np.array([0, 1] * 5))

        aDs = DataSetGeneral.new(X=X, y=y, groups=groups, name="ds1")
        bDs = DataSetGeneral.new(X=X, y=y, groups=groups, name="ds2")
        dsList = [aDs, bDs]
        ds1 = DataSetGeneral.concat(dsList=dsList)
        ds2 = DataSetGeneral.concat(dsList=dsList, creatNewGroupsFromNames=True)

        self.assertFalse(ds1.groups.equals(ds2.groups))  # type: ignore[arg-type]
        self.assertTrue(ds1.X.equals(ds2.X))

        ds1 = DataSetGeneral.new(X=X, y=y, groups=groups, name="ds1")
        ds2 = DataSetGeneral.new(X=X, y=y, name="ds2")
        dsList = [ds1, ds2]
        with self.assertRaises(AssertionError):
            _ = DataSetGeneral.concat(dsList=dsList)

    def test_groupsAndSample(self) -> None:
        X = np.random.rand(10, 3)
        y = np.random.rand(10)
        groups = np.array([0, 1] * 5)

        ds = DataSetGeneral.new(X=X, y=y)
        _ds = ds.sample(2)
        self.assertTrue(_ds.X.shape[0] == 2)
        self.assertTrue(_ds.groups is None)

        ds = DataSetGeneral.new(X=X, y=y, groups=groups)
        _ds = ds.sample(2)
        self.assertTrue(_ds.X.shape[0] == 2)
        self.assertTrue(_ds.groups.shape[0] == 2)

    def test_split_trainTest(self) -> None:
        X = np.random.rand(1000, 3)
        y = np.random.rand(1000)
        groups = np.array([0, 1, 2, 3, 4] * 200)
        groupDs = DataSetGeneral.new(X=X, y=y, groups=groups)
        notGroupDs = DataSetGeneral.new(X=X, y=y)

        trainDs, testDs = groupDs.split_trainTest(
            useGroupsIfPossible=True, useShuffleSplit=False, test_size=0.2
        )
        assert trainDs.X.shape[0] == 800
        assert testDs.X.shape[0] == 200
        assert not set(trainDs.groups) & set(testDs.groups)

        trainDs, testDs = groupDs.split_trainTest(
            useGroupsIfPossible=True, useShuffleSplit=True, test_size=0.2
        )
        assert trainDs.X.shape[0] == 800
        assert testDs.X.shape[0] == 200
        assert not set(trainDs.groups) & set(testDs.groups)

        trainDs, testDs = groupDs.split_trainTest(
            useGroupsIfPossible=False, useShuffleSplit=False, test_size=0.2
        )
        assert trainDs.X.shape[0] == 800
        assert testDs.X.shape[0] == 200
        assert set(trainDs.groups) & set(testDs.groups)

        trainDs, testDs = groupDs.split_trainTest(
            useGroupsIfPossible=False, useShuffleSplit=True, test_size=0.2
        )
        assert trainDs.X.shape[0] == 800
        assert testDs.X.shape[0] == 200
        assert set(trainDs.groups) & set(testDs.groups)

        trainDs, testDs = notGroupDs.split_trainTest(
            useGroupsIfPossible=True, useShuffleSplit=False, test_size=0.2
        )
        assert trainDs.X.shape[0] == 800
        assert testDs.X.shape[0] == 200

        trainDs, testDs = notGroupDs.split_trainTest(
            useGroupsIfPossible=True, useShuffleSplit=True, test_size=0.2
        )
        assert trainDs.X.shape[0] == 800
        assert testDs.X.shape[0] == 200

        trainDs, testDs = notGroupDs.split_trainTest(
            useGroupsIfPossible=False, useShuffleSplit=False, test_size=0.2
        )
        assert trainDs.X.shape[0] == 800
        assert testDs.X.shape[0] == 200

        trainDs, testDs = notGroupDs.split_trainTest(
            useGroupsIfPossible=False, useShuffleSplit=True, test_size=0.2
        )
        assert trainDs.X.shape[0] == 800
        assert testDs.X.shape[0] == 200

        trainDs1, testDs1 = notGroupDs.split_trainTest(
            useGroupsIfPossible=False,
            useShuffleSplit=True,
            test_size=0.2,
            seed=123456789,
        )
        trainDs2, testDs2 = notGroupDs.split_trainTest(
            useGroupsIfPossible=False,
            useShuffleSplit=True,
            test_size=0.2,
            seed=987654321,
        )
        trainDs3, testDs3 = notGroupDs.split_trainTest(
            useGroupsIfPossible=False,
            useShuffleSplit=True,
            test_size=0.2,
            seed=987654321,
        )
        assert not trainDs1.equals(trainDs2)
        assert not testDs1.equals(testDs2)
        assert trainDs3.equals(trainDs2)
        assert testDs3.equals(testDs2)
