import os
import tempfile

from anre.utils import testutil
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.functions import get_randomStr


class TestFileSystem(testutil.TestCase):
    rootDirPath: str

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        rootDirPath = tempfile.mkdtemp()
        cls.rootDirPath = rootDirPath

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        assert cls.rootDirPath
        FileSystem.delete_folder(path=cls.rootDirPath, ignore_errors=True)
        assert not os.path.exists(cls.rootDirPath)

    def test_ensureEndOfLine(self) -> None:
        assert FileSystem.ensure_end_of_line('test') == 'test\n'
        assert FileSystem.ensure_end_of_line('test\n') == 'test\n'
        assert FileSystem.ensure_end_of_line(b'test') == b'test\n'
        assert FileSystem.ensure_end_of_line(b'test\n') == b'test\n'

        with self.assertRaises(ValueError):
            FileSystem.ensure_end_of_line(['test', 'test'])  # type: ignore[arg-type]

    def test_all(self) -> None:
        rootDirPath = self.rootDirPath
        assert rootDirPath

        ### folders create
        # test if can create folder on demand
        working_dir_path = os.path.join(rootDirPath, get_randomStr(30))
        assert not os.path.exists(working_dir_path)
        FileSystem.create_folder(path=working_dir_path)
        assert os.path.exists(working_dir_path)

        deep_dir_path = os.path.join(
            working_dir_path, get_randomStr(5), get_randomStr(5), get_randomStr(5)
        )
        FileSystem.create_folder(path=deep_dir_path)
        assert os.path.exists(deep_dir_path)

        ### files create
        file_name_list = [
            'file_1.txt',
            'file_2.txt',
            'file_3.txt',
            'notFile_4.txt',
            'notFile_5_forDelete.txt',
        ]
        for file_name in file_name_list:
            file_path = os.path.join(deep_dir_path, file_name)
            open(file_path, mode='a').close()

        ### find those files
        glob_pattern = os.path.join(working_dir_path, '**', '*.txt')
        path_list = FileSystem.get_path_list_via_glob(glob_pattern=glob_pattern, recursive=True)
        assert len(path_list) == 5
        path_list.sort()

        FileSystem.delete_file(path_list[-1])
        path_list = FileSystem.get_path_list_via_glob(glob_pattern=glob_pattern, recursive=True)
        assert len(path_list) == 4

        re_pattern = r'.+file_(\d)\.txt$'
        case_id_map_to_path = FileSystem.get_case_id_map_to_path_via_glob_and_re(
            glob_pattern=glob_pattern, re_pattern=re_pattern, recursive=True
        )
        assert len(case_id_map_to_path) == 3

        ### copy folder
        # copy content
        deep_dir_path2 = os.path.join(
            working_dir_path, 'newFolder', 'toTestContentCopy', get_randomStr(5)
        )
        assert not os.path.exists(deep_dir_path2)
        FileSystem.copy_folder(src=deep_dir_path, dst=deep_dir_path2, raise_if_exist=False)
        assert os.path.exists(deep_dir_path2)
        glob_pattern = os.path.join(
            working_dir_path, 'newFolder', 'toTestContentCopy', '**', '*.txt'
        )
        path_list = FileSystem.get_path_list_via_glob(glob_pattern=glob_pattern, recursive=True)
        assert len(path_list) == 4

        # create simlink
        deep_dir_path3 = os.path.join(
            working_dir_path, 'newFolder', 'toTestLinkCopy', get_randomStr(5)
        )
        assert not os.path.exists(deep_dir_path3)
        FileSystem.copy_folder(
            src=deep_dir_path, dst=deep_dir_path3, raise_if_exist=False, symlinks=True
        )
        assert os.path.exists(deep_dir_path3)

        glob_pattern = os.path.join(working_dir_path, 'newFolder', 'toTestLinkCopy', '**', '*.txt')
        path_list = FileSystem.get_path_list_via_glob(glob_pattern=glob_pattern, recursive=True)
        assert len(path_list) == 4

        # sync
        # deepDirPath4 = os.path.join(workingDirPath, 'newFolder', 'testForSync', get_randomStr(5))
        # assert not os.path.exists(deepDirPath4)
        # FileSystem.create_folder(deepDirPath4)  # folder need to exist
        # FileSystem.sync(src=deep_dir_path + '/', dst=deepDirPath4, exclude=['notFile_4.txt'], showProgress=False)  # move content only
        # FileSystem.sync(src=deep_dir_path, dst=deepDirPath4, exclude=['notFile_4.txt'], showProgress=False)  # move with folder
        # assert os.path.exists(deepDirPath4)
        #
        # globPattern = os.path.join(workingDirPath, 'newFolder', 'testForSync', '**', '*.txt')
        # pathList = FileSystem.get_pathList_viaGlob(globPattern=globPattern, recursive=True)
        # assert len(pathList) == 6

        ### copy file
        deep_dir_path5 = os.path.join(
            working_dir_path, 'newFolder', 'toTestFileCopy', get_randomStr(5)
        )
        assert not os.path.exists(deep_dir_path5)
        FileSystem.create_folder(deep_dir_path5)
        new_file_path = os.path.join(deep_dir_path5, 'newFileName.txt')
        FileSystem.copy_file(path_list[0], new_file_path)
        assert os.path.exists(new_file_path)
        FileSystem.delete_file(new_file_path)
        assert not os.path.exists(new_file_path)

        ### test read and write
        # plain
        file_path = os.path.join(deep_dir_path, 'readWrite.txt')
        FileSystem.write_bytes(dumps=b'labas', path=file_path, archive=False)
        assert os.path.exists(file_path)
        assert FileSystem.read_bytes(path=file_path) == b'labas'
        # bz2
        file_path = os.path.join(deep_dir_path, 'readWrite.txt.bz2')
        FileSystem.write_bytes(dumps=b'labas', path=file_path, archive=True)
        assert os.path.exists(file_path)
        assert FileSystem.read_bytes(path=file_path) == b'labas'
        # gz
        file_path = os.path.join(deep_dir_path, 'readWrite.txt.gz')
        FileSystem.write_bytes(dumps=b'labas', path=file_path, archive=True)
        assert os.path.exists(file_path)
        assert FileSystem.read_bytes(path=file_path) == b'labas'

        byte_list = [b'{"labas": "viso"}', b'{"kaip": "sakei?"}']
        file_path = os.path.join(deep_dir_path, 'readWrite_1.jsonl')
        FileSystem.write_bytes(dumps=byte_list, path=file_path, archive=False)
        assert os.path.exists(file_path)
        assert FileSystem.read_bytes(path=file_path) == b'{"labas": "viso"}\n{"kaip": "sakei?"}\n'
        assert tuple(FileSystem.read_byte_lines(path=file_path)) == (
            b'{"labas": "viso"}\n',
            b'{"kaip": "sakei?"}\n',
        )

        byte_list = [b'{"labas": "viso"}\n', b'{"kaip": "sakei?"}\n']
        file_path = os.path.join(deep_dir_path, 'readWrite_2.jsonl')
        FileSystem.write_bytes(dumps=byte_list, path=file_path, archive=False)
        assert os.path.exists(file_path)
        assert FileSystem.read_bytes(path=file_path) == b'{"labas": "viso"}\n{"kaip": "sakei?"}\n'
        assert tuple(FileSystem.read_byte_lines(path=file_path)) == (
            b'{"labas": "viso"}\n',
            b'{"kaip": "sakei?"}\n',
        )

        # scan
        file_label_map_to_paths = FileSystem.get_file_label_map_to_paths(dir_path=deep_dir_path)
        assert isinstance(file_label_map_to_paths, dict)
        assert set(file_label_map_to_paths) == {
            'file_1',
            'file_2',
            'file_3',
            'notFile_4',
            'readWrite',
            'readWrite_1',
            'readWrite_2',
        }

        # clean up
        assert os.path.exists(rootDirPath)
        FileSystem.delete_folder(path=rootDirPath)
        assert not os.path.exists(rootDirPath)
