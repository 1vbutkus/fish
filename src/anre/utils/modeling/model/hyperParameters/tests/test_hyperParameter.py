from anre.utils import testutil
from anre.utils.modeling.model.hyperParameters.hyperParameter import HyperParameter


class TestHyperParameter(testutil.TestCase):
    def test_happyPath(self) -> None:
        _ = HyperParameter(
            label="test",
            type="float",
            value=0,
        )
        _ = HyperParameter(
            label="test",
            type="float",
            value=0,
            hardLims=(0, 10),
            softLims=(0, 10),
            admissibleValues=(0, 1, 2, 3),
        )

    def test_validation(self) -> None:
        with self.assertRaises(AssertionError):
            HyperParameter(
                label="test",
                type="str",
                value=0,
            )

        with self.assertRaises(AssertionError):
            HyperParameter(
                label="test",
                type="float",
                value=0,
                hardLims=(1, 10),
            )

        with self.assertRaises(AssertionError):
            HyperParameter(
                label="test",
                type="float",
                value=0,
                admissibleValues=(1, 2, 3),
            )
