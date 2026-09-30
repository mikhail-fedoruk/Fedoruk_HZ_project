import numpy as np
from dataclasses import dataclass
from typing import Literal



@dataclass(frozen=True)
class Star:
    name: str
    mass_kg: float
    luminosity_w: float

@dataclass(frozen=True)
class KeplerOrbit:
    semi_major_axis_m: float
    eccentricity: float

@dataclass(frozen=True)
class Planet:
    name: str
    orbit: KeplerOrbit

@dataclass(frozen=True)
class ThermalConfig:
    bond_albedo: float
    emissivity: float
    redistribution_factor: float