import pandas as pd

from anre.utils import functions, testutil


class TestFunctions(testutil.TestCase):
    def test_(self) -> None:
        inputStr = 'a,b-c_d1  some 123worl1'
        outputStr = functions.clean_strToAlphanumericOnly(inputStr=inputStr)
        assert outputStr == 'abc_d1some123worl1'

    def test_seqNr(self) -> None:
        sr = pd.Series([0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1])
        actRes = functions.seqNr(sr=sr)
        expRes = pd.Series([0, 1, 0, 1, 2, 0, 0, 0, 0, 0, 1, 2, 0, 1])
        self.assertTrue(actRes.equals(expRes))

    def test_get_randomStr(self) -> None:
        randomStr = functions.get_randomStr(10)
        self.assertIsInstance(randomStr, str)
        self.assertEqual(len(randomStr), 10)

    def test_get_randomWord(self) -> None:
        randomWord = functions.get_randomWord(10)
        self.assertIsInstance(randomWord, str)
        self.assertEqual(len(randomWord), 10)

    def test_get_chunks(self) -> None:
        originalList = list(range(10))
        chunksList = list(functions.chunks(originalList, n=3))
        self.assertEqual(len(chunksList), 4)
        self.assertEqual(originalList, functions.flattenList(chunksList))

    def test_sequentialIdGenerator(self) -> None:
        gnr = functions.sequentialIdGenerator(maxValue=3)
        assert [next(gnr) for _ in range(10)] == [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]
