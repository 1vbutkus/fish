import os
import tempfile

import joblib
import numpy as np
import pandas as pd
from sklearn import linear_model
from sklearn.multioutput import MultiOutputRegressor

from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.sklearn_.transformer.modeler import Modeler


class TestModeler(testutil.TestCase):
    _rootDirPath: str
    X: np.ndarray
    xDf: pd.DataFrame
    mainDirPath: str

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        nRows = 60
        nCols = 5
        X = np.random.rand(nRows, nCols)
        xDf = pd.DataFrame(X, columns=['A', 'B', 'C', 'D', 'E'])

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
        xDf = self.xDf

        model = MultiOutputRegressor(linear_model.HuberRegressor())
        transformer = Modeler(
            model=model,
            x_fields=['A', 'B', 'C'],
            y_fields=['D', 'E'],
        )
        self._test_transformerOnData(
            transformer=transformer,
            X=xDf,
        )

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

        FileSystem.delete_folder(mainDirPath)
