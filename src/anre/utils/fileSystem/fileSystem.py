import bz2
import glob
import gzip
import logging
import os
import platform
import re
import shutil
import warnings
from collections import defaultdict
from pathlib import PureWindowsPath
from typing import Any

from appdirs import user_cache_dir
from cachetools import cached

from anre.utils.process.process import Process

logger = logging.getLogger(__name__)


class FileSystem:
    @classmethod
    def create_folder(
        cls,
        path: str,
        permissions: int = 0o777,
        recreate: bool = False,
        recursive: bool = True,
        raise_if_exists: bool = False,
    ) -> None:
        path = os.path.expanduser(path)

        if recreate and os.path.exists(path):
            shutil.rmtree(path)

        if not os.path.exists(path):
            os.umask(0)
            if recursive:
                os.makedirs(path, mode=permissions)
            else:
                os.mkdir(path, mode=permissions)
        elif raise_if_exists:
            raise FileExistsError(f'File already exists: {path}')

        assert os.path.exists(path), f'create_folder failed. Path does not exist: {path}'

    @classmethod
    def create_os_cache_dir(cls, *args: Any) -> str:
        _path = os.path.join('bird', *args)
        path = user_cache_dir(_path)
        cls.create_folder(path, raise_if_exists=False)
        return path

    @classmethod
    def delete_folder(cls, path: str, ignore_errors: bool = False) -> None:
        path = os.path.expanduser(path)
        shutil.rmtree(path, ignore_errors=ignore_errors)

    @classmethod
    def delete_file(cls, path: str, raise_if_missing: bool = False) -> None:
        path = os.path.expanduser(path)
        if os.path.exists(path):
            os.remove(path)
        elif raise_if_missing:
            raise FileNotFoundError(f'File does not exists: {path}')

        assert not os.path.exists(path), f'delete_file failed. Path still exist: {path}'

    @staticmethod
    def copy_file(
        src: str,
        dst: str,
    ) -> None:
        shutil.copyfile(src, dst)

    @staticmethod
    def rename_file_or_folder(src: str, dst: str) -> None:
        os.rename(src, dst)

    @staticmethod
    def move(src: str, dst: str) -> None:
        shutil.move(src, dst)

    @staticmethod
    def copy_folder(
        src: str, dst: str, symlinks: bool = False, raise_if_exist: bool = True
    ) -> None:
        shutil.copytree(src=src, dst=dst, dirs_exist_ok=not raise_if_exist, symlinks=symlinks)

    @staticmethod
    def sync(
        src: str, dst: str, show_progress: bool = True, exclude: list[str] | None = None
    ) -> None:
        assert os.path.exists(src), f'{src=} does not exist'

        exclude_cmd = ' '.join([f'--exclude {x}' for x in exclude]) if exclude else ''
        progress = '--progress' if show_progress else ''
        cmd = f"rsync {exclude_cmd} -ah --append --partial {progress} {src} {dst} --delete"

        exclude_msg = f' and excluding {exclude}' if exclude else ''
        msg = f'Syncing {src} with {dst} {exclude_msg}'
        logger.info(msg)

        Process.run_withLiveOutput(command=cmd, consumeMsgFn=lambda _msg: print(_msg))

    #    Process.run_withLiveOutput(command=cmd, consumeMsgFn=lambda msg: log.info(msg))

    @classmethod
    def get_path_list_via_glob(cls, glob_pattern: str, recursive: bool = False) -> list[str]:
        return cls.fix_paths(glob.glob(glob_pattern, recursive=recursive))

    @staticmethod
    def fix_path(path: str) -> str:
        if platform.system() in ("Windows", "Microsoft"):
            path = PureWindowsPath(path).as_posix()
        return path

    @classmethod
    def fix_paths(cls, paths: list[str]) -> list[str]:
        if platform.system() in ("Windows", "Microsoft"):
            return [cls.fix_path(p) for p in paths]
        return paths

    @classmethod
    def get_path_list_via_glob_and_re(
        cls, glob_pattern: str, re_pattern: str, recursive: bool = False
    ) -> list[str]:
        pathMatchList = cls.get_path_match_tuple_list(
            glob_pattern=glob_pattern, re_pattern=re_pattern, recursive=recursive
        )
        pathList = [el[0] for el in pathMatchList]
        return pathList

    @classmethod
    def get_case_id_map_to_path_via_glob_and_re(
        cls, glob_pattern: str, re_pattern: str, recursive: bool = False
    ) -> dict:
        pathMatchList = cls.get_path_match_tuple_list(
            glob_pattern=glob_pattern, re_pattern=re_pattern, recursive=recursive
        )
        groupCounts = [len(el[1]) for el in pathMatchList]
        if not groupCounts:
            return {}
        assert (min(groupCounts) == 1) and (max(groupCounts) == 1), (
            'Expecting exactly one value in group. If complex case is needed, please use get_pathMatchTupleList directly.'
        )
        caseIdMapToPath = {el[1][0]: el[0] for el in pathMatchList}
        if len(caseIdMapToPath) < len(pathMatchList):
            ddict = defaultdict(list)
            for el in pathMatchList:
                path = el[0]
                key = el[1][0]
                ddict[key].append(path)

            dubDict = {key: pathList for key, pathList in ddict.items() if len(pathList) > 1}
            msg = f'There are duplicated folders for the same key. Please investigate:\n{dubDict}'
            raise RuntimeError(msg)

        return caseIdMapToPath

    @classmethod
    def get_path_match_tuple_list(
        cls, glob_pattern: str, re_pattern: str, recursive: bool = False
    ) -> list[tuple[str, Any]]:
        """Grazina suporuotuota path ir reIstraukta info.

        list[tuple[path, (rePathGroups)]]
        """
        path_list = cls.get_path_list_via_glob(glob_pattern, recursive=recursive)
        regex = re.compile(re_pattern, flags=0)

        path_match_list = []
        for path in path_list:
            m = regex.match(path)
            if m is None:
                continue
            path_match_list.append((path, m.groups()))

        return path_match_list

    @classmethod
    def get_file_label_map_to_paths(cls, dir_path: str) -> dict[str, list[str]]:
        """Prabrosina direktorija suranda failu su tasku ir paskirsto juos pagal label

        Nuskaito direktorija
        surenka visus failus bent su vienu tasku
        Paadinimas ikipirmotasko yra label.

        Grazina:
        {
            'label1': ['path1'],
            'label2': ['path2a', 'path2b'],
        }
        """
        path_match_tuple_list = cls.get_path_match_tuple_list(
            glob_pattern=os.path.join(dir_path, '*.*'),
            re_pattern=r'.*/(.+?)\.(.+)',
            recursive=False,
        )

        file_label_map_to_paths: dict[str, list[str]] = {}
        for path_match_tuple in path_match_tuple_list:
            path, (label, bigExt) = path_match_tuple
            val = file_label_map_to_paths.get(label)
            if val is None:
                file_label_map_to_paths[label] = [path]
            elif isinstance(val, list):
                val.append(path)
            else:
                raise ValueError

        return file_label_map_to_paths

    @classmethod
    def write_bytes(
        cls, dumps: bytes | list[bytes], path: str, archive: bool, overwrite: bool = False
    ) -> None:
        # overwrite
        if os.path.exists(path):
            if overwrite:
                FileSystem.delete_file(path=path, raise_if_missing=False)
            else:
                raise FileExistsError(f'File already exists, use overwrite if needed. Path: {path}')

        # make su folder exist
        FileSystem.create_folder(path=os.path.dirname(path))

        ### save
        _, extension = os.path.splitext(path)
        if archive:
            if extension == '.gz':
                with gzip.open(path, 'wb') as fh:
                    cls._writeToFileHandler(dumps=dumps, fh=fh)
            elif extension == '.bz2':
                with bz2.BZ2File(path, 'wb') as fh:
                    cls._writeToFileHandler(dumps=dumps, fh=fh)
            else:
                raise NotImplementedError(
                    f'Unsupported archive extension ({extension}). Available values: [.gz, .bz2]'
                )
        else:
            if extension in ['.gz', '.bz2']:
                msg = f'archive={archive}, but extension(`{extension}`) presumes archive'
                warnings.warn(msg)
            with open(path, "wb") as fh:
                cls._writeToFileHandler(dumps=dumps, fh=fh)

    @classmethod
    def get_file_metadata_str_for_cache_reload(cls, path: str) -> str:
        fileStats = os.stat(path)

        # a change to file access time should not invalidate the cache since reading does not change the contents
        exludedFields = ['st_atime', 'st_atime_ns']
        metadata = {
            x: fileStats.__getattribute__(x)
            for x in fileStats.__dir__()
            if 'st_' in x and x not in exludedFields
        }
        return str(metadata)

    @classmethod
    def read(
        cls, path: str, mode: str = 'r', read_lines: bool = False, cache: bool = False
    ) -> bytes | list[bytes] | str | list[str]:
        if cache:
            metadataStr = cls.get_file_metadata_str_for_cache_reload(path)
            return cls._read_cache(
                path=path, mode=mode, read_lines=read_lines, metadata_str=metadataStr
            )
        else:
            return cls._read(path=path, mode=mode, read_lines=read_lines)

    @classmethod
    def read_bytes(cls, path: str, cache: bool = False) -> bytes:
        return cls.read(path=path, mode='rb', read_lines=False, cache=cache)  # type: ignore[return-value]

    @classmethod
    def read_byte_lines(cls, path: str, cache: bool = False) -> list[bytes]:
        return cls.read(path=path, mode='rb', read_lines=True, cache=cache)  # type: ignore[return-value]

    @classmethod
    def read_to_str(cls, path: str, mode: str = 'r', cache: bool = False) -> str:
        contents = cls.read(path=path, mode=mode, cache=cache)
        return ''.join(contents)  # type: ignore[arg-type]

    @classmethod
    @cached({})
    def _read_cache(
        cls, path: str, mode: str, read_lines: bool, metadata_str: str
    ) -> bytes | list[bytes] | str | list[str]:
        # The metadataStr is used to skip caching when the file gets updated. If the files changes, the metadata
        # will change, and we will reread the file instead of returning an outdated copy.
        return cls._read(path=path, mode=mode, read_lines=read_lines)

    @classmethod
    def _read(
        cls, path: str, mode: str, read_lines: bool = False
    ) -> bytes | list[bytes] | str | list[str]:
        assert os.path.exists(path), f'File not found in FileSystem.readBytes.Path: {path}'
        _, extension = os.path.splitext(path)
        assert mode in ['r', 'rb']

        obj: bytes | list[bytes] | str | list[str]
        if extension == '.gz':
            with gzip.open(path, mode=mode) as fh:
                if read_lines:
                    obj = fh.readlines()
                else:
                    obj = fh.read()
        elif extension == '.bz2':
            with bz2.BZ2File(path, mode=mode) as fh:  # type: ignore[call-overload]
                if read_lines:
                    obj = fh.readlines()
                else:
                    obj = fh.read()
        else:
            with open(path, mode) as fh:
                if read_lines:
                    obj = fh.readlines()
                else:
                    obj = fh.read()

        return obj

    @classmethod
    def _chmod_recursive(cls, path: str, dir_mode: int, file_mode: int) -> None:
        assert os.path.exists(path), f'path does not exist: {path}'
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                os.chmod(dirpath, dir_mode)
                for filename in filenames:
                    os.chmod(os.path.join(dirpath, filename), file_mode)
        elif os.path.isfile(path):
            os.chmod(path, file_mode)

    @classmethod
    def chmod_read_only(cls, path: str) -> None:
        cls._chmod_recursive(path=path, dir_mode=0o555, file_mode=0o444)

    @classmethod
    def chmod_all_permissions(cls, path: str) -> None:
        cls._chmod_recursive(path=path, dir_mode=0o777, file_mode=0o777)

    @classmethod
    def _writeToFileHandler(cls, dumps: bytes | list[bytes], fh) -> None:
        if isinstance(dumps, bytes):
            fh.write(dumps)
        elif isinstance(dumps, list):
            if dumps:
                firstDump = dumps[0]
                lastDump = dumps[-1]
                assert isinstance(firstDump, bytes), (
                    f'dumps must be bytes or list of bytes. Got element of `{type(firstDump)}` that is not supported.'
                )
                assert isinstance(lastDump, bytes), (
                    f'dumps must be bytes or list of bytes. Got element of `{type(lastDump)}` that is not supported.'
                )
                efl = b'\n'
                assert firstDump.endswith(efl) == lastDump.endswith(efl), (
                    'First and last element has different end of line seperator'
                )
                if firstDump.endswith(efl):
                    dumps = b''.join(dumps)
                else:
                    dumps = b'\n'.join(dumps) + b'\n'
                fh.write(dumps)
                # alternativly we can run: dumps = [cls.ensureEndOfLine(dump) for dump in dumps], but it has performance risks
            else:
                fh.writelines(dumps)
        else:
            raise ValueError(
                f'dumps must be bytes or list of bytes. Type `{type(dumps)}` is not supported.'
            )

    @staticmethod
    def ensure_end_of_line(data_rec: bytes | str) -> bytes | str:
        """Uztikrina, kad dataRec gale butu end of line zymeklis"""
        if isinstance(data_rec, str):
            efl = '\n'
            if data_rec.endswith(efl):
                return data_rec
            else:
                return data_rec + efl
        elif isinstance(data_rec, bytes):
            eflb = b'\n'
            if data_rec.endswith(eflb):
                return data_rec
            else:
                return data_rec + eflb
        else:
            msg = f'dataRec is type of {type(data_rec)}, but exected str or bite'
            raise ValueError(msg)


def copy_file_with_relative_path(src_path: str, src_root_dir: str, dst_dir: str) -> str:
    rel_path = os.path.relpath(src_path, src_root_dir)
    dst_path = os.path.join(dst_dir, rel_path)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    shutil.copy2(src_path, dst_path)
    return dst_path
