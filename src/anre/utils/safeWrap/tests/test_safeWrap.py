# mypy: disable-error-code="list-item"
from anre.utils import testutil
from anre.utils.safeWrap.safeWrap import SafeWrap
from anre.utils.safeWrap.safeWrapResult import SafeWrapResult
from anre.utils.worker.worker import Worker


class TestSafeWrap(testutil.TestCase):
    def test_wrapFun_basicFunctions(self) -> None:
        def foo(x, y):
            print("----aaaa----")
            return x + y

        fooSave = SafeWrap.decorator()(foo)
        saveWrapResults = fooSave(5, 5)
        self.assertIsInstance(saveWrapResults, SafeWrapResult)
        self.assertTrue(saveWrapResults.success)
        self.assertEqual(saveWrapResults.result, 10)

        with self.assertWarns(Warning):
            saveWrapResults = fooSave(5, 'a')
            self.assertIsInstance(saveWrapResults, SafeWrapResult)
            self.assertTrue(not saveWrapResults.success)
            self.assertTrue(isinstance(saveWrapResults.result, BaseException))

        fooSave = SafeWrap.decorator(verbose=False)(foo)
        saveWrapResults = fooSave(5, 'a')
        self.assertIsInstance(saveWrapResults, SafeWrapResult)
        self.assertTrue(not saveWrapResults.success)
        self.assertTrue(isinstance(saveWrapResults.result, BaseException))

    def test_safeStarmap_basicFunctions(self) -> None:
        def foo(x, y):
            return x + y

        worker = Worker.new_sequential()

        resExp = [2, 3, 4]
        resList = SafeWrap.safeStarmap(foo, [1, 2, 3], y=1, worker=worker)
        resList = SafeWrap.get_resultsList(wrappedResultList=resList)
        self.assertEqual(resExp, resList)

        with self.assertWarns(Warning):
            resExp = [2, 3, None]
            resList = SafeWrap.safeStarmap(foo, [1, 2, 'a'], y=1, worker=worker)
            resList = SafeWrap.get_resultsList(wrappedResultList=resList, objIfFailed=None)
            self.assertEqual(resExp, resList)

    def test_safeStarmap_multiArguments(self) -> None:
        def foo(x, y, z):
            return x + y + z

        worker = Worker.new_sequential()

        resExp = [3, 5, 7]
        resList = SafeWrap.safeStarmap(foo, [(1, 1), (2, 2), (3, 3)], z=1, worker=worker)
        resList = SafeWrap.get_resultsList(wrappedResultList=resList, objIfFailed=None)
        self.assertEqual(resExp, resList)

        resList = SafeWrap.safeStarmap(
            foo,
            kwargsList=[{'x': 1, 'y': 1}, {'x': 2, 'y': 2}, {'x': 3, 'y': 3}],
            z=1,
            worker=worker,
        )
        resList = SafeWrap.get_resultsList(wrappedResultList=resList, objIfFailed=None)
        self.assertEqual(resExp, resList)

        resExp = [3, 5, None]
        with self.assertWarns(Warning):
            resList = SafeWrap.safeStarmap(foo, [(1, 1), (2, 2), (3, 'a')], z=1, worker=worker)
            resList = SafeWrap.get_resultsList(wrappedResultList=resList, objIfFailed=None)
            self.assertEqual(resExp, resList)

        with self.assertWarns(Warning):
            resList = SafeWrap.safeStarmap(
                foo,
                kwargsList=[{'x': 1, 'y': 1}, {'x': 2, 'y': 2}, {'x': 3, 'y': 'a'}],
                z=1,
                worker=worker,
            )
            resList = SafeWrap.get_resultsList(wrappedResultList=resList, objIfFailed=None)
            self.assertEqual(resExp, resList)
