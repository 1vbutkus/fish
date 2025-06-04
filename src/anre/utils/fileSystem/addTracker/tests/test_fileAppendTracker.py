import os
import tempfile

from anre.utils import testutil
from anre.utils.fileSystem.addTracker.fileAppendTracker import FileAppendTracker
from anre.utils.fileSystem.fileSystem import FileSystem


class TestfileAppendTracker(testutil.TestCase):
    rootDirPath: str

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        rootDirPath = tempfile.mkdtemp()
        cls.rootDirPath = rootDirPath

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        assert cls.rootDirPath is not None
        FileSystem.delete_folder(path=cls.rootDirPath, ignore_errors=True)
        assert not os.path.exists(cls.rootDirPath)

    def test_happyPath(self) -> None:
        rootDirPath = self.rootDirPath
        assert rootDirPath is not None

        filePath = os.path.join(rootDirPath, 'file1.log')
        with open(filePath, 'w') as f:
            f.write('Very first line.\n')
            f.write('Second line with WARNING\n')

        fileAppendTracker = FileAppendTracker(filePath=filePath)
        newLines = fileAppendTracker.get_newLines()
        assert isinstance(newLines, list)
        assert len(newLines) == 2

        newLines = fileAppendTracker.get_newLines()
        assert isinstance(newLines, list)
        assert len(newLines) == 0

        with open(filePath, 'a') as f:
            f.write('New line.\n')

        newLines = fileAppendTracker.get_newLines()
        assert isinstance(newLines, list)
        assert len(newLines) == 1

        FileSystem.delete_file(filePath)

        with self.assertWarns(Warning):
            _ = fileAppendTracker.get_newLines()

        with open(filePath, 'a') as f:
            f.write('Very first line with ERROR.\n')
        newLines = fileAppendTracker.get_newLines()
        assert isinstance(newLines, list)
        assert len(newLines) == 1

        assert fileAppendTracker.get_lastRowCount() == 1
        assert fileAppendTracker.get_logLevelCounts() == {'WARNING': 1, 'ERROR': 1, 'CRITICAL': 0}
