import numpy as np

# ==================================================
# ФИЗИЧЕСКИЕ КОНСТАНТЫ
# ==================================================

AU_M = 149_597_870_700.0   # https://cneos.jpl.nasa.gov/glossary/au.html
DAY_S = 86_400.0
YEAR_S = 365.25 * DAY_S    # https://science.nasa.gov/earth/facts/

G = 6.67430e-11            # https://en.wikipedia.org/wiki/Gravitational_constant
SIGMA_SB = 5.670374419e-8  # https://en.wikipedia.org/wiki/Stefan%E2%80%93Boltzmann_law

M_SUN_KG = 1.98e30         # https://solarscience.msfc.nasa.gov/
L_SUN_W = 3.846e26         # https://solarscience.msfc.nasa.gov/
R_SUN_M = 695_990_000      # https://solarscience.msfc.nasa.gov/
EARTH_FLUX_W_M2 = 1361     # https://earth.gsfc.nasa.gov/climate/projects/solar-irradiance/science

# ==================================================
# ФУНКЦИИ ПЕРЕВОДА РАЗМЕРНОСТЕЙ
# ==================================================

def _checked_scale(value, scale):
    with np.errstate(over='raise', invalid='raise'):
        result = np.multiply(value, scale)
    if not np.all(np.isfinite(result)):
        raise ValueError('После перевода единиц получилось неконечное число.')
    return result


def au_to_m(value_au: float | np.ndarray) -> float | np.ndarray:
    return _checked_scale(value_au, AU_M)

def m_to_au(value_m: float | np.ndarray) -> float | np.ndarray:
    return value_m / AU_M

def days_to_seconds(value_days: float | np.ndarray) -> float | np.ndarray:
    return value_days * DAY_S

def seconds_to_days(value_s: float | np.ndarray) -> float | np.ndarray:
    return value_s / DAY_S

def years_to_seconds(value_years: float | np.ndarray) -> float | np.ndarray:
    return value_years * YEAR_S

def seconds_to_years(value_s: float | np.ndarray) -> float | np.ndarray:
    return value_s / YEAR_S

def solar_mass_to_kg(value: float | np.ndarray) -> float | np.ndarray:
    return value * M_SUN_KG

def kg_to_solar_mass(value: float | np.ndarray) -> float | np.ndarray:
    return value / M_SUN_KG

def solar_luminosity_to_watt(value: float | np.ndarray) -> float | np.ndarray:
    return _checked_scale(value, L_SUN_W)

def watt_to_solar_luminosity(value: float | np.ndarray) -> float | np.ndarray:
    return value / L_SUN_W