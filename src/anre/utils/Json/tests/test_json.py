# mypy: disable-error-code="assignment"
import os
import tempfile

import numpy as np

from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.Json.Json import Json


class TestJson(testutil.TestCase):
    rootDirPath: str = None
    dirPath: str

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        rootDirPath = tempfile.mkdtemp()
        dirPath = os.path.join(rootDirPath, 'someDir', 'deeperDir')
        cls.rootDirPath = rootDirPath
        cls.dirPath = dirPath

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        FileSystem.delete_folder(path=cls.rootDirPath, ignore_errors=True)
        assert not os.path.exists(cls.rootDirPath)

    def test_dumpsDefault_hardcodedConsts(self) -> None:
        assert Json.dumps("aaa") == b'"aaa"'
        assert Json.dumps(["aaa", 'bbb']) == b'["aaa","bbb"]'
        assert Json.dumps({'list': ["aaa", 'bbb']}) == b'{"list":["aaa","bbb"]}'

    def test_dumpsToStr_hardcodedConsts(self) -> None:
        assert Json.dumps_to_str("aaa") == '"aaa"'
        assert Json.dumps_to_str(["aaa", 'bbb']) == '["aaa","bbb"]'
        assert Json.dumps_to_str({'list': ["aaa", 'bbb']}) == '{"list":["aaa","bbb"]}'

    def test_linesDumps_hardcodedConsts(self) -> None:
        objOrg = [{'1': 1}, {'2': 2}, {'3': 3}]
        assert Json.linesDumps(objOrg) == [b'{"1":1}\n', b'{"2":2}\n', b'{"3":3}\n']
        assert Json.lines_dumps_to_str(objOrg) == ['{"1":1}\n', '{"2":2}\n', '{"3":3}\n']

    def test_loadsAndDumps_returningProperties_various(self) -> None:
        objOrg = {'list': ["aaa", 'bbb'], '2': {'1': 1, '2': 1}}
        objAlt = Json.loads(Json.dumps(objOrg))
        assert objAlt is not objOrg
        assert objAlt == objOrg

    def test_loadsAndDumps_returningProperties_list(self) -> None:
        objOrg = ["aaa", 'bbb']
        objAlt = Json.lines_loads(Json.linesDumps(objOrg))
        assert objAlt is not objOrg
        assert objAlt == objOrg

    def test_loadsAndDumps_returningProperties_list_of_dicts(self) -> None:
        objOrg = [{'1': 1}, {'2': 2}, {'3': 3}]
        objAlt = Json.lines_loads(Json.linesDumps(objOrg))
        assert objAlt is not objOrg
        assert objAlt == objOrg

    def test_loadAndDumpToFile_returningProperties(self) -> None:
        dirPath = self.dirPath
        objOrg = [{'1': 1}, {'2': 2}, {'3': 3}]

        filePath = os.path.join(dirPath, 'data.json')
        Json.dump(obj=objOrg, path=filePath, overwrite=True)
        objAlt = Json.load(path=filePath)
        assert objAlt is not objOrg
        assert objAlt == objOrg

        filePath = os.path.join(dirPath, 'data.json')
        Json.dump(obj=objOrg, path=filePath, overwrite=True, useIndent=True)
        objAlt = Json.load(path=filePath)
        assert objAlt is not objOrg
        assert objAlt == objOrg

        filePath = os.path.join(dirPath, 'data.jsonl')
        Json.linesDump(objList=objOrg, path=filePath, overwrite=True)
        objAlt = Json.linesLoad(path=filePath)
        assert objAlt is not objOrg
        assert objAlt == objOrg

        filePath = os.path.join(dirPath, 'data.json.gz')
        Json.dump(obj=objOrg, path=filePath, overwrite=True, useIndent=True, archive=True)
        objAlt = Json.load(path=filePath)
        assert objAlt is not objOrg
        assert objAlt == objOrg

        filePath = os.path.join(dirPath, 'data.jsonl.bz2')
        Json.linesDump(objList=objOrg, path=filePath, overwrite=True, archive=True)
        objAlt = Json.linesLoad(path=filePath)
        assert objAlt is not objOrg
        assert objAlt == objOrg

    def test_loadAndDumpToFile_numpy(self) -> None:
        dirPath = self.dirPath
        objOrg = [{'1': [np.nan]}, {'2': np.ndarray([1, 2, 3])}, {'3': 3}]

        filePath = os.path.join(dirPath, 'data_numpy.json')
        Json.dump(obj=objOrg, path=filePath, overwrite=True, useNumpy=True)
        objAlt = Json.load(path=filePath)
        assert objAlt is not objOrg
        assert objAlt[0]['1'][0] is None
        assert (objAlt[1]['2'] == objOrg[1]['2']).all()  # type: ignore[index]
        assert objAlt[2] == objOrg[2]
