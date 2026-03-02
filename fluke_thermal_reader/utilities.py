"""Temperature scaling and unit conversions for thermal data."""

import numpy as np


def scale_uint16_to_temperature(raw: np.ndarray, T_min: float, T_max: float) -> np.ndarray:
    """Map raw [0, 65535] to [T_min, T_max] °C (linear)."""
    raw = np.asarray(raw, dtype=np.float64)
    return T_min + raw * (T_max - T_min) / 65535.0


def counts_to_temperature_linear(counts: np.ndarray, *, count_min=None, count_max=None, T_min=None, T_max=None, background_temp=20.0) -> np.ndarray:
    """Linear rescale counts to °C; uses min/max from array or metadata, else range around background_temp."""
    count_min = float(np.nanmin(counts)) if count_min is None else count_min
    count_max = float(np.nanmax(counts)) if count_max is None else count_max
    if T_min is None:
        T_min = background_temp - 20.0
    if T_max is None:
        T_max = background_temp + 35.0
    if count_max <= count_min:
        return np.full_like(counts, background_temp, dtype=np.float64)
    return T_min + (counts.astype(np.float64) - count_min) / (count_max - count_min) * (T_max - T_min)


def calc_equation(z, x):
    """Polynomial: sum of z[i] * x^(len(z)-1-i). Used for calibration curve."""
    k = range(0, len(z))
    m = k[::-1]
    y = 0
    for i in k:
        y += np.multiply(z[i], x ** m[i])
    return y


class UnitConversion:
    """Temperature and unit conversions (K↔°C, °C↔°F, etc.)."""

    @staticmethod
    def k2c(k):
        return k - 273.15

    @staticmethod
    def c2k(c):
        return c + 273.15

    @staticmethod
    def c2n(c):
        return c * (33.0 / 100.0)

    @staticmethod
    def n2c(n):
        return n * (100.0 / 33.0)

    @staticmethod
    def c2f(c, diff=False):
        """Celsius to Fahrenheit; diff=True for delta conversion."""
        return c * (9.0 / 5.0) + (0 if diff else 32)

    @staticmethod
    def f2c(f, diff=False):
        """Fahrenheit to Celsius; diff=True for delta conversion."""
        return (f - (0 if diff else 32)) * (5.0 / 9.0)

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
