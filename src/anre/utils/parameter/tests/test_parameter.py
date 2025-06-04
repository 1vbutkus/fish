# mypy: disable-error-code="var-annotated"
import os
from pathlib import PurePath

from anre.utils import testutil
from anre.utils.parameter.parameter import Parameter


class TestParameters(testutil.TestCase):
    pathToPredefined: str
    dotDict1: dict
    mixDict1: dict
    dict1: dict
    dotDict2: dict
    dict2: dict
    emptyParameters: Parameter
    predefinedParameters: Parameter
    parametersDotDict1: Parameter
    parametersMixDict1: Parameter
    parametersDict1: Parameter
    parametersDotDict2: Parameter
    parametersDict2: Parameter
    predefinedSet1: dict
    predefinedSet2: dict
    predefinedSet3: dict

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.pathToPredefined = str(
            PurePath(os.path.abspath(__file__)).parent.joinpath('resources', 'predefined.yaml')
        )

        cls.emptyParameters = Parameter()
        cls.predefinedParameters = Parameter(pathToPredefined=cls.pathToPredefined)

        cls.predefinedSet1 = {
            'a.b1': 1,
            'a.b2': 2,
            'a.b3': None,
            'a.b4': None,
            'a.b5': {},
            'a.b6': [],
            'c.d.e': 3,
        }
        cls.predefinedSet2 = {'a': 1}
        cls.predefinedSet3 = {'b': 2}

        cls.dotDict1 = {
            'a.b.c1.d1': 1,
            'a.b.c1.d2': 2,
            'a.b.c1.d3': 3,
            'a.b.c2.d.e': -1,
            'b': [4, 44, 444],
            'c': 5,
            'd': None,
        }
        cls.mixDict1 = {
            'a.b': {'c1.d1': 1, 'c1.d2': 2, 'c1.d3': 3, 'c2': {'d': {'e': -1}}},
            'b': [4, 44, 444],
            'c': 5,
            'd': None,
        }
        cls.dict1 = {
            'a': {'b': {'c1': {'d1': 1, 'd2': 2, 'd3': 3}, 'c2': {'d': {'e': -1}}}},
            'b': [4, 44, 444],
            'c': 5,
            'd': None,
        }
        cls.dotDict2 = {'a': 1, 'b': {}, 'c': None}
        cls.dict2 = {'a': 1, 'b': {}, 'c': None}

        cls.parametersDotDict1 = Parameter(cls.dotDict1)
        cls.parametersMixDict1 = Parameter(cls.mixDict1)
        cls.parametersDict1 = Parameter(cls.dict1)
        cls.parametersDotDict2 = Parameter(cls.dotDict2)
        cls.parametersDict2 = Parameter(cls.dict2)

    def test_inList(self) -> None:
        baseParam = {
            'const0_1': 1,
            'const0_2': 1,
            'dict0': {
                'int': 1,
                'float': 2.0,
                'chose': 'abc',
                'extra': 'extra',
                'list': [
                    {'a': 1},
                    {'b': 2},
                    {'c': 3},
                ],
            },
        }
        _ = Parameter(baseParam)

    def test_newDefaultParametersShouldBeEmpty(self) -> None:
        self.assertDictEqual({}, self.emptyParameters.paramDotDict)

    def test_allPredefinedParameterSetsShouldBeReturned(self) -> None:
        self.assertDictEqual(
            self.predefinedSet1, self.predefinedParameters.set('PredefinedSet1').paramDotDict
        )
        self.assertDictEqual(
            self.predefinedSet2, self.predefinedParameters.set('PredefinedSet2').paramDotDict
        )
        self.assertDictEqual(
            self.predefinedSet3, self.predefinedParameters.set('PredefinedSet3').paramDotDict
        )

    def test_nestedPredefinedParametersShouldBeSupported(self) -> None:
        self.assertDictEqual(
            {'a': 1, 'b': 2}, self.predefinedParameters.set('PredefinedSet4').paramDotDict
        )
        self.assertDictEqual(
            {'a': 1, 'b': 2, 'c': 999}, self.predefinedParameters.set('PredefinedSet5').paramDotDict
        )

    def test_deeperLevelShouldNotBeSupported(self) -> None:
        # jei bandoma giliau naudoti predifinu , tai nerui viekti,nesgreitaibusgalimap pradeti maisytis
        self.assertDictEqual(
            {'a': ['PredefinedSet2', {'c': 999}]},
            self.predefinedParameters.set('PredefinedSet6').paramDotDict,
        )

    def test_parameterObjectShouldBeValidInput(self) -> None:
        self.assertEqual(self.parametersDotDict1, Parameter(self.parametersDotDict1))
        self.assertEqual(self.parametersDotDict2, Parameter(self.parametersDotDict2))
        self.assertEqual(self.parametersMixDict1, Parameter(self.parametersMixDict1))

    def test_parameterListShouldBeValidInput(self) -> None:
        expRes12 = {'a': 1, 'c.d.e': 3}
        actRes12 = self.predefinedParameters.set(['PredefinedSet1', 'PredefinedSet2']).paramDotDict
        self.assertDictEqual(expRes12, actRes12)

        expRes21 = {
            'a.b1': 1,
            'a.b2': 2,
            'a.b3': None,
            'a.b4': None,
            'a.b5': {},
            'a.b6': [],
            'c.d.e': 3,
        }
        actRes21 = self.predefinedParameters.set(['PredefinedSet2', 'PredefinedSet1']).paramDotDict
        self.assertDictEqual(expRes21, actRes21)

        expRes13 = {
            'a.b1': 1,
            'a.b2': 2,
            'a.b3': None,
            'a.b4': None,
            'a.b5': {},
            'a.b6': [],
            'b': 2,
            'c.d.e': 3,
        }
        actRes13 = self.predefinedParameters.set(['PredefinedSet1', 'PredefinedSet3']).paramDotDict
        self.assertDictEqual(expRes13, actRes13)

        expRes31 = {
            'a.b1': 1,
            'a.b2': 2,
            'a.b3': None,
            'a.b4': None,
            'a.b5': {},
            'a.b6': [],
            'b': 2,
            'c.d.e': 3,
        }
        actRes31 = self.predefinedParameters.set(['PredefinedSet3', 'PredefinedSet1']).paramDotDict
        self.assertDictEqual(expRes31, actRes31)

        expRes23 = {'a': 1, 'b': 2}
        actRes23 = self.predefinedParameters.set(['PredefinedSet2', 'PredefinedSet3']).paramDotDict
        self.assertDictEqual(expRes23, actRes23)

        expRes32 = {'a': 1, 'b': 2}
        actRes32 = self.predefinedParameters.set(['PredefinedSet3', 'PredefinedSet2']).paramDotDict
        self.assertDictEqual(expRes32, actRes32)

    def test_parameterArgsWithMixedTypesShouldBeAValidInput(self) -> None:
        expRes312 = {'a': 1, 'b': 2, 'c.d.e': 3}
        actRes312 = self.predefinedParameters.set(
            self.predefinedSet3, [['PredefinedSet1', 'PredefinedSet2']]
        ).paramDotDict
        self.assertDictEqual(expRes312, actRes312)

        expRes123 = {'a': 1, 'b': 2, 'c.d.e': 3}
        actRes123 = self.predefinedParameters.set([
            self.predefinedSet3,
            ['PredefinedSet1', 'PredefinedSet2'],
        ]).paramDotDict
        self.assertDictEqual(expRes123, actRes123)

        expRes123Z = {'a': 1, 'b': 2, 'c.d.e': 3, 'z.z': 9}
        actRes123Z = self.predefinedParameters.set(
            ['PredefinedSet1', 'PredefinedSet2'], self.predefinedSet3, {'z': {'z': 9}}
        ).paramDotDict
        self.assertDictEqual(expRes123Z, actRes123Z)

        expResZ123 = {'a': 1, 'b': 2, 'c.d.e': 3, 'z.z': 9}
        actResZ123 = self.predefinedParameters.set(
            [{'z': {'z': 9}}, ['PredefinedSet1', 'PredefinedSet2']], self.predefinedSet3
        ).paramDotDict
        self.assertDictEqual(expResZ123, actResZ123)

        expResPrm = {'a': 0, 'b': 2, 'c.d.e': 3, 'q': 9}
        actResPrm = self.predefinedParameters.set(
            self.predefinedSet3,
            [['PredefinedSet1', 'PredefinedSet2'], Parameter({'q': 9})],
            Parameter({'a': 0}),
        ).paramDotDict
        self.assertDictEqual(expResPrm, actResPrm)

    def test_passingInDuplicatedParametersShouldReturnTheOriginalOne(self) -> None:
        self.assertDictEqual(
            self.predefinedSet1, Parameter(self.predefinedSet1, self.predefinedSet1).paramDotDict
        )
        self.assertDictEqual(
            self.predefinedSet2, Parameter(self.predefinedSet2, self.predefinedSet2).paramDotDict
        )
        self.assertDictEqual(
            self.predefinedSet3, Parameter(self.predefinedSet3, self.predefinedSet3).paramDotDict
        )
        self.assertDictEqual(
            self.predefinedSet1,
            self.predefinedParameters.set(['PredefinedSet1', 'PredefinedSet1']).paramDotDict,
        )
        self.assertDictEqual(
            self.predefinedSet2,
            self.predefinedParameters.set(['PredefinedSet2', 'PredefinedSet2']).paramDotDict,
        )
        self.assertDictEqual(
            self.predefinedSet3,
            self.predefinedParameters.set(['PredefinedSet3', 'PredefinedSet3']).paramDotDict,
        )

    def test_dotDictWithOverlappingKeysShouldNotBeALegalParameter(self) -> None:
        with self.assertRaises(AssertionError):
            Parameter({'a.b.c': 1, 'a.b.c.d': 2})
        with self.assertRaises(AssertionError):
            Parameter({'a.b.c.d': 1, 'a.b.c': 2})

    def test_parametersDotDictAndDictShouldBeInvariant(self) -> None:
        self.assertDictEqual(self.dict1, self.parametersDict1.paramDict)
        self.assertDictEqual(self.dict1, self.parametersDotDict1.paramDict)
        self.assertDictEqual(self.dict1, self.parametersMixDict1.paramDict)
        self.assertDictEqual(self.dotDict1, self.parametersDict1.paramDotDict)
        self.assertDictEqual(self.dotDict1, self.parametersDotDict1.paramDotDict)
        self.assertDictEqual(self.dotDict1, self.parametersMixDict1.paramDotDict)

        self.assertDictEqual(self.dict2, self.parametersDict2.paramDict)
        self.assertDictEqual(self.dict2, self.parametersDotDict2.paramDict)
        self.assertDictEqual(self.dotDict2, self.parametersDict2.paramDotDict)
        self.assertDictEqual(self.dotDict2, self.parametersDotDict2.paramDotDict)

        self.assertDictEqual(
            self.parametersDict1.paramDotDict, self.parametersDotDict1.paramDotDict
        )
        self.assertDictEqual(
            self.parametersDict1.paramDotDict, self.parametersMixDict1.paramDotDict
        )
        self.assertDictEqual(
            self.parametersDotDict1.paramDotDict, self.parametersMixDict1.paramDotDict
        )

        self.assertDictEqual(self.parametersDict1.paramDict, self.parametersDotDict1.paramDict)
        self.assertDictEqual(self.parametersDict1.paramDict, self.parametersMixDict1.paramDict)
        self.assertDictEqual(self.parametersDotDict1.paramDict, self.parametersMixDict1.paramDict)

    def test_parameterHashShouldBeDeterministic(self) -> None:
        h = self.parametersDict1.hash()
        for _ in range(1000):
            self.assertEqual(h, Parameter(self.dotDict1).hash())

    def test_differentParametersShouldNotBeEqual(self) -> None:
        self.assertNotEqual(self.parametersDict1, self.parametersDict2)
        self.assertNotEqual(self.parametersDotDict1, self.parametersDotDict2)

    def test_differentParameterHashesShouldNotBeEqual(self) -> None:
        self.assertNotEqual(self.parametersDict1.hash(), self.parametersDict2.hash())
        self.assertNotEqual(self.parametersDotDict1.hash(), self.parametersDotDict2.hash())

    def test_settingWithAnEmptyDictShouldNotChangeAnything(self) -> None:
        self.assertEqual(self.parametersDict1, self.parametersDict1.set())
        self.assertEqual(self.parametersDotDict1, self.parametersDotDict1.set())
        self.assertEqual(self.parametersDict2, self.parametersDict2.set())
        self.assertEqual(self.parametersDotDict2, self.parametersDotDict2.set())

    def test_settingSomethingShouldUpdateThatValue(self) -> None:
        newParameters = self.parametersDict1.set({'a': 1, 'b.a': 2})
        self.assertEqual(1, newParameters['a'])
        self.assertEqual(1, newParameters.paramDotDict['a'])
        self.assertEqual(1, newParameters.paramDict['a'])
        self.assertEqual(2, newParameters['b.a'])
        self.assertEqual(2, newParameters.paramDotDict['b.a'])
        self.assertEqual(2, newParameters.paramDict['b']['a'])
        self.assertEqual({'a': 2}, newParameters['b'])

    def test_droppingSomethingShouldDeleteIt(self) -> None:
        prm = self.parametersDict1.drop('a')
        self.assertDictEqual({'b': [4, 44, 444], 'c': 5, 'd': None}, prm.paramDict)

    def test_droppingTheLastElementOfSomeBranchShouldLeaveAnEmptyDict(self) -> None:
        prm = self.parametersDict1.drop('a.b')
        self.assertDictEqual({'a': {}, 'b': [4, 44, 444], 'c': 5, 'd': None}, prm.paramDict)

    def test_droppingNonExistingParameterShouldChangeNothing(self) -> None:
        prm = self.parametersDict1.drop('abc', raiseIfMissing=False)
        self.assertDictEqual(self.parametersDict1.paramDict, prm.paramDict)

    def test_droppingNonExistingParameterShouldRaiseByDefault(self) -> None:
        with self.assertRaises(KeyError):
            self.parametersDict1.drop('abc', raiseIfMissing=True)

    def test_convertingBetweenDotDictAndDictShouldNotChangeAnyValuesOrTypes(self) -> None:
        prm = Parameter(Parameter(self.parametersDotDict1.paramDotDict).paramDict)
        self.assertDictEqual(self.parametersDotDict1.paramDotDict, prm.paramDotDict)
        self.assertDictEqual(self.parametersDotDict1.paramDict, prm.paramDict)

    def test_convertingBetweenDictAndDotDictShouldNotChangeAnyValuesOrTypes(self) -> None:
        prm = Parameter(Parameter(self.parametersDotDict1.paramDict).paramDotDict)
        self.assertDictEqual(self.parametersDotDict1.paramDotDict, prm.paramDotDict)
        self.assertDictEqual(self.parametersDotDict1.paramDict, prm.paramDict)

    def test_valuesInDotDictShouldBeEqualToValuesInDict(self) -> None:
        prms = [self.parametersDotDict1, self.parametersDotDict2]
        for prm in prms:
            for dotDictKey, dotDictValue in prm.paramDotDict.items():
                paramsDict = prm.paramDict
                for key in dotDictKey.split('.'):
                    paramsDict = paramsDict[key]
                self.assertEqual(dotDictValue, paramsDict)

    def test_valuesInDictShouldBeEqualToValuesInDotDict(self) -> None:
        def checkRecursively(paramsDict, dotDictKey, prm):
            if type(paramsDict) is dict and len(paramsDict) > 0:
                for k, v in paramsDict.items():
                    nestedKey = k if dotDictKey == '' else f'{dotDictKey}.{k}'
                    checkRecursively(v, nestedKey, prm)
            else:
                self.assertEqual(paramsDict, prm.paramDotDict[dotDictKey])

        prms = [self.parametersDotDict1, self.parametersDotDict2]
        for prm in prms:
            checkRecursively(prm.paramDict, '', prm)

    def test_gettingAnUnsetParameterKeyShouldRaise(self) -> None:
        with self.assertRaises(KeyError):
            _ = self.parametersDict1['q']
        with self.assertRaises(KeyError):
            _ = self.parametersDict1['q.q']
        with self.assertRaises(KeyError):
            _ = self.parametersDict2['q']

    def test_gettingASetParameterKeyShouldNotRaise(self) -> None:
        _ = self.parametersDict1['a']
        _ = self.parametersDict1['a.b']
        _ = self.parametersDict2['b']

    def test_parametersWithoutADerivedDotDictFunShouldHaveEmptyDerivedDicts(self) -> None:
        self.assertDictEqual({}, self.parametersDict1.paramDerivedDotDict)
        self.assertDictEqual({}, self.parametersDict1.paramDerivedDict)

    def test_parametersGetterAskedForAPartialParameterShouldReturnItAsADict(self) -> None:
        self.assertDictEqual(
            {'c1': {'d1': 1, 'd2': 2, 'd3': 3}, 'c2': {'d': {'e': -1}}},
            self.parametersDotDict1['a.b'],
        )

    # def test_printingParametersShouldPreserveQuotes(self) -> None:
    #     self.assertEqual("Derived parameters:\n{}\nBase parameters:\n{\n  'x': '\"text in double quotes\"'\n}", repr(Parameter({'x': '"text in double quotes"'})))
    #     self.assertEqual("Derived parameters:\n{}\nBase parameters:\n{\n  'x': \"'text in single quotes'\"\n}", repr(Parameter({'x': "'text in single quotes'"})))
    #
    # def test_printingParametersShouldPreserveNoneValue(self) -> None:
    #     self.assertEqual("Derived parameters:\n{}\nBase parameters:\n{\n  'x': None\n}", repr(Parameter({'x': None})))
    #
    # def test_printingParametersShouldPreserveEmptyDict(self) -> None:
    #     self.assertEqual("Derived parameters:\n{}\nBase parameters:\n{\n  'x': {}\n}", repr(Parameter({'x': {}})))
    #
    # def test_printingParametersShouldPreserveCurlyBracketsAndSpacesInString(self) -> None:
    #     self.assertEqual("Derived parameters:\n{}\nBase parameters:\n{\n  'x': 'abc{}{}{{}}   {}{}'\n}", repr(Parameter({'x': 'abc{}{}{{}}   {}{}'})))

    def test_aaa(self) -> None:
        prm = Parameter({'a': {'b': {'c': 1, 'd': 2, 'e': 3}}})
        assert prm.set({'a.b.c': -99})['a.b'] == {'c': -99, 'd': 2, 'e': 3}
        assert prm.set({'a.b': {'newValues': [1, 2, 3]}})['a.b'] == {
            'c': 1,
            'd': 2,
            'e': 3,
            'newValues': [1, 2, 3],
        }
