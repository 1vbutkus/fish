from anre.utils import testutil
from anre.utils.worker.tests.nest import double_in_nest


class TestWorkerNest(testutil.TestCase):
    def test_argsOnly(self) -> None:
        x_list_list = [
            [1, 2, 3],
            [4, 5, 6],
        ]
        res_exp = [[2, 4, 6], [8, 10, 12]]
        res_act = double_in_nest(x_list_list=x_list_list, allowedNest=True)
        assert res_exp == res_act

        with self.assertRaises(AssertionError):
            _ = double_in_nest(x_list_list=x_list_list, allowedNest=False)
