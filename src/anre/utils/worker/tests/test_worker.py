# mypy: disable-error-code="operator"
from os import cpu_count

from anre.utils import testutil
from anre.utils.worker.worker import Worker


def fun_outside(x):
    return x + 1


class TestWorker(testutil.TestCase):
    workers: list[Worker]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        maxWorker = max(1, cpu_count() - 6)

        cls.workers = [
            Worker.new(),
            Worker.new_sequential(),
            Worker.new_thread(),
            Worker.new_multiproc(max_worker=maxWorker),
            Worker.new_joblib(max_worker=maxWorker),
            Worker.new_sequential(show_progress=True),
            Worker.new_thread(max_worker=maxWorker, show_progress=True),
            Worker.new_multiproc(max_worker=maxWorker, show_progress=True),
            Worker.new_joblib(max_worker=maxWorker, show_progress=True),
        ]

    def test_argsOnly(self) -> None:
        for worker in self.workers:
            resExp1 = [1, 2, 3]
            mapResAct1 = worker.map(self._fun1, [1, 2, 3])
            starMapResAct1 = worker.starmap(self._fun1, [1, 2, 3])
            self.assertEqual(resExp1, mapResAct1)
            self.assertEqual(resExp1, starMapResAct1)

            resExp2 = [5, 7, 9]
            mapResAct2 = worker.map(self._fun2, [1, 2, 3], [4, 5, 6])
            starMapResAct2 = worker.starmap(self._fun2, [(1, 4), (2, 5), (3, 6)])
            self.assertEqual(resExp2, mapResAct2)
            self.assertEqual(resExp2, starMapResAct2)

    def test_kwargsOnly(self) -> None:
        for worker in self.workers:
            resExp1 = [1, 2, 3]
            mapResAct1 = worker.map(self._fun1, a=[1, 2, 3])
            starMapResAct1 = worker.starmap(self._fun1, kwargs_list=[{'a': 1}, {'a': 2}, {'a': 3}])
            self.assertEqual(resExp1, mapResAct1)
            self.assertEqual(resExp1, starMapResAct1)

            resExp2 = [5, 7, 9]
            mapResAct2 = worker.map(self._fun2, a=[1, 2, 3], b=[4, 5, 6])
            starMapResAct2 = worker.starmap(
                self._fun2, kwargs_list=[{'a': 1, 'b': 4}, {'a': 2, 'b': 5}, {'a': 3, 'b': 6}]
            )
            self.assertEqual(resExp2, mapResAct2)
            self.assertEqual(resExp2, starMapResAct2)

    def test_argsAndKwargs(self) -> None:
        for worker in self.workers:
            resExp2 = [5, 7, 9]
            mapResAct2 = worker.map(self._fun2, [1, 2, 3], b=[4, 5, 6])
            starMapResAct2 = worker.starmap(
                self._fun2, [1, 2, 3], kwargs_list=[{'b': 4}, {'b': 5}, {'b': 6}]
            )
            self.assertEqual(resExp2, mapResAct2)
            self.assertEqual(resExp2, starMapResAct2)

    def test_argsAndConstKwargs(self) -> None:
        for worker in self.workers:
            resExp2 = [2, 3, 4]
            mapResAct2 = worker.map(self._fun2, [1, 2, 3], b=worker.const(1))
            starMapResAct2 = worker.starmap(self._fun2, [1, 2, 3], b=1)
            self.assertEqual(resExp2, mapResAct2)
            self.assertEqual(resExp2, starMapResAct2)

    def test_full(self) -> None:
        for worker in self.workers:
            resExp3 = [8.0, 10.0, 12.0]
            iterArg = [0.5, 1, 1.5]
            mapResAct3 = worker.map(
                self._fun3_withIterArg, [1, 2, 3], b=[4, 5, 6], iterArg=worker.const(iterArg)
            )
            starMapResAct3 = worker.starmap(
                self._fun3_withIterArg,
                [1, 2, 3],
                kwargs_list=[{'b': 4}, {'b': 5}, {'b': 6}],
                iterArg=iterArg,
            )
            self.assertEqual(resExp3, mapResAct3)
            self.assertEqual(resExp3, starMapResAct3)

    def test_functionOutside(self) -> None:
        worker = Worker.new_multiproc()
        worker.starmap(fun_outside, kwargs_list=[{'x': 1}, {'x': 2}])

    @staticmethod
    def _fun1(a):
        return a

    @staticmethod
    def _fun2(a, b):
        return a + b

    @staticmethod
    def _fun3_withIterArg(a, b, iterArg):
        return a + b + sum(iterArg)
