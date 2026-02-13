import numpy as np


def calc_equation(z, x):
    """
    y = calc_equation(z, x)
    Input z, list of function variables
    """
    k = range(0, len(z))
    m = k[::-1]
    y = 0
    for i in k:
        y += np.multiply(z[i], x ** m[i])
    return y


class UnitConversion:
    """Unit conversions (temperature and others). Use: UnitConversion.c2k(t), UnitConversion.k2c(t), etc."""

    @staticmethod
    def k2c(k):
        """Convert Kelvin to Celsius: c = k2c(k)"""
        return k - 273.15

    @staticmethod
    def c2k(c):
        """Convert Celsius to Kelvin: k = c2k(c)"""
        return c + 273.15

    @staticmethod
    def c2n(c):
        """Convert Celsius to Newton: n = c2n(c)"""
        return c * (33.0 / 100.0)

    @staticmethod
    def n2c(n):
        """Convert Newton to Celsius: c = n2c(n)"""
        return n * (100.0 / 33.0)

    @staticmethod
    def c2f(c, diff=False):
        """Celsius to Fahrenheit. Per differenza: c2f(dc, diff=True)"""
        f = c * (9.0 / 5.0)
        if not diff:
            f += 32
        return f

    @staticmethod
    def f2c(f, diff=False):
        """Fahrenheit to Celsius. Per differenza: f2c(df, diff=True)"""
        if not diff:
            f -= 32
        return f * (5.0 / 9.0)

    @staticmethod
    def gpm2lpm(gpm):
        """Gallons per minute to liters per minute"""
        return gpm * 3.785412

    @staticmethod
    def lpm2gpm(lpm):
        return lpm / 3.785412

    @staticmethod
    def psi2bar(psi):
        return psi / 14.50377

    @staticmethod
    def bar2psi(bar):
        return bar * 14.50377

    @staticmethod
    def ft2psi(ft):
        return ft * 0.43352750192825

    @staticmethod
    def psi2ft(psi):
        return psi / 0.43352750192825

    @staticmethod
    def unitlabel(unit):
        if unit == 'C':
            return r'$^\circ$C'
        if unit == 'K':
            return 'K'
        if unit == 'F':
            return r'$^\circ$F'
        if unit == 'N':
            return r'$^\circ$N'
        return None
