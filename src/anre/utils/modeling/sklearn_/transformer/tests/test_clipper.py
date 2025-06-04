import os
import tempfile

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.sklearn_.transformer.clipper import Clipper


class TestClipper(testutil.TestCase):
    _rootDirPath: str
    X: np.ndarray
    xDf: pd.DataFrame
    mainDirPath: str

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        nRows = 60
        nCols = 3
        X = np.random.rand(nRows, nCols)
        xDf = pd.DataFrame(X)

        rootDirPath = tempfile.mkdtemp(suffix=None, prefix=None, dir=None)
        mainDirPath = os.path.join(rootDirPath, 'someDir', 'deeperDir')

        cls.X = X
        cls.xDf = xDf
        cls.mainDirPath = mainDirPath
        cls._rootDirPath = rootDirPath

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        FileSystem.delete_folder(path=cls._rootDirPath, ignore_errors=True)
        assert not os.path.exists(cls._rootDirPath)

    def test_ClipTransformer_smokeTest(self) -> None:
        X = self.X
        xDf = self.xDf

        for _X in [X, xDf]:
            self._test_transformerOnData(transformer=Clipper(), X=_X)
            self._test_transformerOnData(transformer=Clipper(a_min=0.1, a_max=0.9), X=_X)
            self._test_transformerOnData(transformer=Clipper(q_min=0.1, q_max=0.9), X=_X)
            self._test_transformerOnData(transformer=Clipper(q_min=0.1, q_max=None), X=_X)
            self._test_transformerOnData(
                transformer=Clipper(a_min=[0.1, 0.2, 0.3], a_max=0.9), X=_X
            )
            self._test_transformerOnData(
                transformer=Clipper(a_min=[0.1, 0.2, 0.3], q_max=None), X=_X
            )
            self._test_transformerOnData(
                transformer=Clipper(q_min=[0.1, 0.2, 0.3], q_max=None), X=_X
            )

    def test_StandardScaler(self) -> None:
        X = self.X
        xDf = self.xDf

        self._test_transformerOnData(transformer=StandardScaler(), X=X)
        self._test_transformerOnData(transformer=StandardScaler(), X=xDf)

    def _test_transformerOnData(self, transformer, X):
        mainDirPath = self.mainDirPath

        FileSystem.create_folder(mainDirPath)

        transformer.fit(X)
        xTrans = transformer.transform(X)

        _filePath = os.path.join(mainDirPath, 'transformer.joblib')
        assert not os.path.exists(_filePath)
        joblib.dump(transformer, _filePath)
        assert os.path.exists(_filePath)
        transformer2 = joblib.load(_filePath)

        xTrans2 = transformer2.transform(X)
        self.assertTrue(np.all(xTrans == xTrans2))

        pipe = Pipeline([('a', StandardScaler()), ('b', transformer)])
        pipe.fit(X)
        _ = pipe.transform(X)

        FileSystem.delete_folder(mainDirPath)


# self = TestClipper()
# self.setUpClass()
