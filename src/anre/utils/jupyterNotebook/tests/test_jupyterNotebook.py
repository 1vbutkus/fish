import os
import tempfile

import papermill as pm

from anre.config.config import config as anreConfig
from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.jupyterNotebook.jupyterNotebook import JupyterNotebook


class TestJupyterNotebook(testutil.TestCase):
    dirPath: str
    resourceDirPath: str
    rootDirPath: str

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        rootDirPath = tempfile.mkdtemp()
        dirPath = os.path.join(rootDirPath, 'someDir', 'deeperDir')

        resourceDirPath = anreConfig.path.get_path_to_root_dir(
            'src/anre/utils/jupyterNotebook/tests/resources'
        )
        assert os.path.exists(resourceDirPath), f'resourceDirPath does not exist: {resourceDirPath}'

        cls.rootDirPath = rootDirPath
        cls.dirPath = dirPath
        cls.resourceDirPath = resourceDirPath

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        FileSystem.delete_folder(path=cls.rootDirPath, ignore_errors=True)
        assert not os.path.exists(cls.rootDirPath)

    def test_happyPath_ipynb(self) -> None:
        resourceDirPath = self.resourceDirPath
        dirPath = self.dirPath

        templateFilePath = os.path.join(resourceDirPath, 'happyPath.ipynb')
        outputFilePath = os.path.join(dirPath, 'report1.ipynb')
        fileList = JupyterNotebook.run_jupyterTemplate(
            templateFilePath=templateFilePath,
            outputFilePath=outputFilePath,
            parameters=dict(x=1, y=1),
            override=False,
            convertToHtml=True,
            asReport=False,
        )
        self.assertEqual(len(fileList), 2)

        with self.assertRaises(FileExistsError):
            _ = JupyterNotebook.run_jupyterTemplate(
                templateFilePath=templateFilePath,
                outputFilePath=outputFilePath,
                parameters=dict(x=1, y=1),
                override=False,
                convertToHtml=True,
                asReport=False,
            )

        fileList = JupyterNotebook.run_jupyterTemplate(
            templateFilePath=templateFilePath,
            outputFilePath=outputFilePath,
            parameters=dict(x=1, y=1),
            override=True,
            convertToHtml=True,
            asReport=True,
        )
        self.assertEqual(len(fileList), 2)

    def test_happyPath_py(self) -> None:
        resourceDirPath = self.resourceDirPath
        dirPath = self.dirPath

        templateFilePath = os.path.join(resourceDirPath, 'happyPath.py')
        outputFilePath = os.path.join(dirPath, 'report2.ipynb')
        fileList = JupyterNotebook.run_jupyterTemplate(
            templateFilePath=templateFilePath,
            outputFilePath=outputFilePath,
            parameters=dict(x=1, y=1),
            override=False,
            convertToHtml=True,
            asReport=False,
        )
        self.assertEqual(len(fileList), 2)

        with self.assertRaises(FileExistsError):
            _ = JupyterNotebook.run_jupyterTemplate(
                templateFilePath=templateFilePath,
                outputFilePath=outputFilePath,
                parameters=dict(x=1, y=1),
                override=False,
                convertToHtml=True,
                asReport=False,
            )

        fileList = JupyterNotebook.run_jupyterTemplate(
            templateFilePath=templateFilePath,
            outputFilePath=outputFilePath,
            parameters=dict(x=1, y=1),
            override=True,
            convertToHtml=True,
            asReport=True,
        )
        self.assertEqual(len(fileList), 2)

    def test_assertError_py(self) -> None:
        resourceDirPath = self.resourceDirPath
        dirPath = self.dirPath

        templateFilePath = os.path.join(resourceDirPath, 'assertError.py')
        outputFilePath = os.path.join(dirPath, 'report_withError.ipynb')
        with self.assertRaises(pm.exceptions.PapermillExecutionError):
            _ = JupyterNotebook.run_jupyterTemplate(
                templateFilePath=templateFilePath,
                outputFilePath=outputFilePath,
                parameters=dict(x=1, y=1),
                override=False,
                convertToHtml=True,
                asReport=False,
            )
