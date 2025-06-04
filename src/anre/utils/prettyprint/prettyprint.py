from itertools import takewhile

import black
import yaml
from more_itertools import ilen


class PrettyPrint:
    @classmethod
    def get_objectStr(cls, obj: object) -> str:
        className = obj.__class__.__name__
        fieldList = yaml.dump(obj, default_flow_style=False, sort_keys=False, width=160)
        indentedFieldList = ["  " + f for f in fieldList.splitlines(keepends=True)]
        return f"{className}:\n{''.join(indentedFieldList)}\n"

    @classmethod
    def get_dictStr(cls, obj: dict, indent: int = 4) -> str:
        assert type(obj) is dict
        assert indent >= 0
        formatted = black.format_str(
            str(obj), mode=black.Mode(line_length=1, string_normalization=False)
        )
        # formatted = black.format_str(str(obj), mode=black.FileMode(line_length=1, string_normalization=False))
        indentFormattedLines = [
            ' ' * (ilen(takewhile(str.isspace, x)) // 4) * indent + x.lstrip()
            for x in formatted.splitlines()
        ]
        indentFormatted = '\n'.join(indentFormattedLines)
        return indentFormatted

    @classmethod
    def get_listStr(cls, obj: list, indent: int = 4) -> str:
        assert type(obj) is list
        assert indent >= 0
        formatted = black.format_str(
            str(obj), mode=black.Mode(line_length=1, string_normalization=False)
        )
        # formatted = black.format_str(str(obj), mode=black.FileMode(line_length=1, string_normalization=False))
        indentFormattedLines = [
            ' ' * (ilen(takewhile(str.isspace, x)) // 4) * indent + x.lstrip()
            for x in formatted.splitlines()
        ]
        indentFormatted = '\n'.join(indentFormattedLines)
        return indentFormatted

    @classmethod
    def get_tupleStr(cls, obj: tuple, indent: int = 4) -> str:
        assert type(obj) is tuple
        assert indent >= 0
        formatted = black.format_str(
            str(obj), mode=black.Mode(line_length=1, string_normalization=False)
        )
        # formatted = black.format_str(str(obj), mode=black.FileMode(line_length=1, string_normalization=False))
        indentFormattedLines = [
            ' ' * (ilen(takewhile(str.isspace, x)) // 4) * indent + x.lstrip()
            for x in formatted.splitlines()
        ]
        indentFormatted = '\n'.join(indentFormattedLines)
        return indentFormatted


if __name__ == '__main__':
    PrettyPrint.get_dictStr({1: [1, 2, 3]})
