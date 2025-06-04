# mypy: disable-error-code="var-annotated"
from anre.utils import testutil
from anre.utils.prettyprint.prettyprint import PrettyPrint


class TestPrettyPrint(testutil.TestCase):
    def test_get_dictStr_shouldCorrectlyFormatDict(self) -> None:
        someDict = {
            1: 1,
            "abc": {
                "1": {
                    3.4: None,
                },
                None: {},
                'list': [
                    1,
                    2,
                    3,
                ],
            },
        }

        # Note that quotation marks are irrelevant
        someDictExp = (
            "{\n"
            "    1: 1,\n"
            "    'abc': {\n"
            "        '1': {\n"
            "            3.4: None\n"
            "        },\n"
            "        None: {},\n"
            "        'list': [\n"
            "            1,\n"
            "            2,\n"
            "            3,\n"
            "        ],\n"
            "    },\n"
            "}"
        )
        someDictAct = PrettyPrint.get_dictStr(someDict)
        self.assertEqual(someDictExp, someDictAct)

        someDictTwoIndentExp = (
            "{\n"
            "  1: 1,\n"
            "  'abc': {\n"
            "    '1': {\n"
            "      3.4: None\n"
            "    },\n"
            "    None: {},\n"
            "    'list': [\n"
            "      1,\n"
            "      2,\n"
            "      3,\n"
            "    ],\n"
            "  },\n"
            "}"
        )
        someDictTwoIndentAct = PrettyPrint.get_dictStr(someDict, indent=2)
        self.assertEqual(someDictTwoIndentExp, someDictTwoIndentAct)

    def test_get_listStr_shouldCorrectlyFormatList(self) -> None:
        someList = [
            1,
            'abc',
            None,
            [
                1,
                {},
            ],
            [],
            (),
        ]

        someListExp = (
            "[\n"
            "    1,\n"
            "    'abc',\n"
            "    None,\n"
            "    [\n"
            "        1,\n"
            "        {},\n"
            "    ],\n"
            "    [],\n"
            "    (),\n"
            "]"
        )

        someListAct = PrettyPrint.get_listStr(someList, indent=4)
        self.assertEqual(someListExp, someListAct)

    def test_get_tupleStr_shouldCorrectlyFormatTuple(self) -> None:
        someTuple = (
            1,
            'abc',
            None,
            [
                1,
                {},
            ],
            [],
            (),
        )

        someTupleExp = (
            "(\n"
            "    1,\n"
            "    'abc',\n"
            "    None,\n"
            "    [\n"
            "        1,\n"
            "        {},\n"
            "    ],\n"
            "    [],\n"
            "    (),\n"
            ")"
        )

        someTupleAct = PrettyPrint.get_tupleStr(someTuple, indent=4)
        self.assertEqual(someTupleExp, someTupleAct)
