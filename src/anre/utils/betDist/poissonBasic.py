import numpy as np
from scipy.stats import gamma as statsGamma
from scipy.stats import poisson as statsPoisson


class PoissonBasic:
    """This set of cunctions calculates mu -> prob -> ratio -> mu

    In add cases input can be scalar or np array or pd.Series
    The fastes way is np.array

    n corespnds of goalsTogo. And it operates bydefinition P(x <= n) So if you put 2.5 or 2.25 or 2. - all ield the same output.
    """

    @staticmethod
    def get_mu(ratio, n, lowerTail: bool = True):
        """Atvirkstine funkcija

        Patiuninguota greiciaui. Bet yra apribojimas: 0.5, 1.5, 2.5, ...

        Jei naudojam pd, tai dar greiciau kreipianti per Ser.values"""

        prob = lowerTail * (1.0 - 1.0 / ratio) + (1.0 - 1.0 * lowerTail) * 1.0 / ratio
        return statsGamma.ppf(q=prob, a=np.floor(n) + 1)

    @classmethod
    def get_prob(cls, n, mu, lowerTail: bool = True):
        """Tikimybiu funkcija

        Patiuninguota greiciaui. Bet yra apribojimas: 0.5, 1.5, 2.5, ... ir lowerTail in True, False (or 1, 0)

        Jei naudojam pd, tai dar greiciau kreipianti per Ser.values"""

        return np.where(lowerTail, cls.get_prob_under(n=n, mu=mu), cls.get_prob_over(n=n, mu=mu))

    @classmethod
    def get_ratio(cls, n, mu, lowerTail: bool = True):
        return 1.0 / cls.get_prob(n=n, mu=mu, lowerTail=lowerTail)

    @staticmethod
    def get_prob_under(n, mu):
        """Gets P(x <= n)

        n and mu can be scalars or vector (if both vectors, size must match)
        """
        return 1.0 * statsPoisson.cdf(k=np.floor(n), mu=mu)

    @staticmethod
    def get_prob_over(n, mu):
        """Gets P(x > n)

        n and mu can be scalars or vector (if both vectors, size must match)
        """
        return 1.0 - 1.0 * statsPoisson.cdf(k=np.floor(n), mu=mu)

    @staticmethod
    def get_prob_eq(n, mu):
        """Gets P(x == n)

        n and mu can be scalars or vector (if both vectors, size must match)
        """
        return 1.0 * statsPoisson.pmf(k=np.floor(n), mu=mu)
