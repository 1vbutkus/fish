import numpy as np

from anre.utils import testutil
from anre.utils.betDist.poissonBasic import PoissonBasic


class TestFunctions(testutil.TestCase):
    def test_scalarsCycle(self) -> None:
        n = 2.5
        mu = 1.9
        prob_lower = PoissonBasic.get_prob(n=n, mu=mu, lowerTail=True)
        prob_upper = PoissonBasic.get_prob(n=n, mu=mu, lowerTail=False)
        self.assertAlmostEqual(prob_lower + prob_upper, 1)

        ratio_lower = PoissonBasic.get_ratio(n=n, mu=mu, lowerTail=True)
        ratio_upper = PoissonBasic.get_ratio(n=n, mu=mu, lowerTail=False)
        self.assertAlmostEqual(1 / ratio_lower + 1 / ratio_upper, 1)
        self.assertAlmostEqual(1 / ratio_lower, prob_lower)
        self.assertAlmostEqual(1 / ratio_upper, prob_upper)

        mu1 = PoissonBasic.get_mu(ratio=ratio_lower, n=n, lowerTail=True)
        mu2 = PoissonBasic.get_mu(ratio=ratio_upper, n=n, lowerTail=False)
        self.assertAlmostEqual(mu1, mu2)
        self.assertAlmostEqual(mu1, mu)

    def test_vectorCycle(self) -> None:
        n = np.array([2.5, 1.5, 0.5])
        mu = np.array([1.9, 4.0, 0.2])
        lowerTail = np.array([True, True, False])  # type: ignore[arg-type]
        prob = PoissonBasic.get_prob(n=n, mu=mu, lowerTail=lowerTail)  # type: ignore[arg-type]
        ratio = PoissonBasic.get_ratio(n=n, mu=mu, lowerTail=lowerTail)  # type: ignore[arg-type]
        self.assertTrue(np.max(np.abs(1.0 / ratio - prob)) < 1e-6)

        mu1 = PoissonBasic.get_mu(ratio=ratio, n=n, lowerTail=lowerTail)  # type: ignore[arg-type]
        self.assertTrue(np.max(np.abs(mu1 - mu)) < 1e-6)
