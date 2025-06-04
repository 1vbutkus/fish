import os
import tempfile
from dataclasses import dataclass

from anre.utils import testutil
from anre.utils.dataclass_type_validator import dataclass_validate
from anre.utils.dataStructure.info import InfoBase
from anre.utils.fileSystem.fileSystem import FileSystem


class TestInfo(testutil.TestCase):
    dirPath: str
    rootDirPath: str

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        rootDirPath = tempfile.mkdtemp()
        dirPath = os.path.join(rootDirPath, 'someDir', 'deeperDir')
        cls.dirPath = dirPath
        cls.rootDirPath = rootDirPath

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        FileSystem.delete_folder(path=cls.rootDirPath, ignore_errors=True)
        assert not os.path.exists(cls.rootDirPath)

    def test_smoke_happyPath(self) -> None:
        dirPath = self.dirPath

        @dataclass_validate
        @dataclass(frozen=True, repr=False, kw_only=True)
        class Info(InfoBase):
            className: str
            version: str
            gitHash: str
            name: str

        info = Info(
            className='a',
            version='b',
            gitHash='c',
            name='d',
        )
        info.save(dirPath=dirPath, overwrite=True)
        info2 = Info.load(dirPath=dirPath)

        self.assertTrue(info == info2)
        self.assertFalse(info is info2)

    def test_tuple(self) -> None:
        dirPath = self.dirPath

        @dataclass_validate
        @dataclass(frozen=True, repr=False, kw_only=True)
        class Info(InfoBase):
            className: str
            version: str
            gitHash: str
            name: str
            tupleVar: tuple

        info = Info(
            className='a',
            version='b',
            gitHash='c',
            name='d',
            tupleVar=(
                'a',
                'b',
            ),
        )
        info.save(dirPath=dirPath, overwrite=True)
        info2 = Info.load(dirPath=dirPath)

        self.assertTrue(info == info2)
        self.assertFalse(info is info2)

    def test_isConvertable_happyPath(self) -> None:
        dataDict = {
            'a': dict(aa=1, bb=2, bc=3),
            'b': [1, 2, 3],
            'c': (1, 2, 3),
        }
        assert InfoBase.check_ifDictIsConvertable(dataDict)

    def test_isConvertable_badCases(self) -> None:
        class CustomObject:
            pass

        obj = CustomObject()
        dataDict = {
            'obj': obj,
        }
        assert not InfoBase.check_ifDictIsConvertable(dataDict)
