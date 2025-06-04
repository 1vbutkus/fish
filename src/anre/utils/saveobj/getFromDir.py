import os
from typing import Any

from anre.utils.fileSystem import FileSystem
from anre.utils.saveobj import saveobj


def get_obj_fromDirPathAndLabel(
    dirPath: str, label: str | None, raiseIfMissing=True
) -> Any | dict[str, Any]:
    if raiseIfMissing:
        assert os.path.exists(dirPath), f'path does not exist: {dirPath}'

    if label is None:
        pathMatchTupleList = FileSystem.get_path_match_tuple_list(
            glob_pattern=os.path.join(dirPath, '*.*'),
            re_pattern=r'.*/(.+)\.(.+)',
            recursive=False,
        )
        labelList = [pathMatchTuple[1][0] for pathMatchTuple in pathMatchTupleList]
        objDict = {
            _label: _get_obj_fromDirPathAndLabel_single(
                dirPath=dirPath, label=_label, raiseIfMissing=raiseIfMissing
            )
            for _label in labelList
        }
        return objDict
    else:
        return _get_obj_fromDirPathAndLabel_single(
            dirPath=dirPath, label=label, raiseIfMissing=raiseIfMissing
        )


def _get_obj_fromDirPathAndLabel_single(
    dirPath: str, label: str, raiseIfMissing=True
) -> Any | None:
    ### filePath
    pathMatchTupleList = FileSystem.get_path_match_tuple_list(
        glob_pattern=os.path.join(dirPath, '*.*'),
        re_pattern=rf'.*/({label})\.([^/]+)',
        recursive=False,
    )
    if len(pathMatchTupleList) == 1:
        filePath = pathMatchTupleList[0][0]
    elif len(pathMatchTupleList) > 1:
        filePaths = [pathMatchTuple[0] for pathMatchTuple in pathMatchTupleList]
        msg = f'label({label}) has several files. The result is ambiguous: {filePaths}'
        raise AssertionError(msg)
    else:
        if raiseIfMissing:
            msg = f'filePath does not exist for label `{label}`. dirPath: {dirPath}'
            raise FileNotFoundError(msg)
        return None

    ### load object
    assert os.path.exists(filePath), (
        f'File was found, but do not exist anymore. Somthing is wrong: {filePath}'
    )
    return saveobj.load(path=filePath)
