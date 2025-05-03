import math

import numpy as np
import pandas as pd

from Bus import Bus
from Bundle import Bundle
from Geometry import Geometry
from Conductor import Conductor
from Settings import s


def get_zbase(vbase, sbase):
    """return Zbase"""
    return vbase**2/sbase


class TransmissionLine:
    def __init__(self, name: str, bus1: Bus, bus2: Bus, bundle: Bundle, geometry: Geometry, length: float):
        """Initialize a TransmissionLine instance with given parameters."""
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.bundle = bundle
        self.geometry = geometry
        self.length = length
        self.zbase = get_zbase(bus1.base_kv, s.base_power)

        # Calculate series impedance and shunt admittance
        self.series_impedance = self.calculate_series_impedance()
        self.shunt_admittance = self.calculate_shunt_admittance()
        self.yprim = self.calc_yprim()

    def calculate_series_impedance(self):
        """Calculate the series impedance of the transmission line."""
        Ra = (self.bundle.conductor.resistance/self.bundle.num_conductors  * self.length) /self.zbase
        Xa = (2*math.pi*s.frequency * 2e-7 * math.log(self.geometry.DEQ / self.bundle.DSL) * 1609  * self.length)/self.zbase # ohm
        return complex(Ra, Xa)

    def calculate_shunt_admittance(self):
        """Calculate the shunt admittance of the transmission line."""
        y = (2*math.pi*s.frequency * 1609 * 2 * math.pi * 8.854e-12 / math.log(self.geometry.DEQ / self.bundle.DSC) * self.length)*self.zbase
        return complex(0, y)


    def __str__(self):
        """Return a formatted string representing the transmission line object."""
        return (
            f"Transmission Line: {self.name}\n"
            f"Connected Buses: {self.bus1} <--> {self.bus2}\n"
            f"Bundle: {self.bundle}\n"
            f"Geometry: {self.geometry}\n"
            f"Length: {self.length} km\n"
            f"Series Impedance: {self.series_impedance} pu\n"
            f"Shunt Admittance: {self.shunt_admittance} pu\n"
            f"Y-Primitive Matrix: {self.yprim}"
        )

    # primitive matrix: diagonals are admittance connected to node, off-diagonals are negative of admittance btw nodes
    def calc_yprim(self):

        # stored impedance and admittance are ohm values. Per-unitize here
        y_series = 1 / self.series_impedance  if self.series_impedance != 0 else float('inf')
        y_shunt = self.shunt_admittance
        return np.array([[y_series + y_shunt/2, -y_series], [-y_series, y_series + y_shunt/2]])



if __name__ == "__main__":
    """
    TransmissionLine Validation
    """

    bus1 = Bus("Bus 1", 20)
    bus2 = Bus("Bus 2", 230)

    conductor1 = Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
    bundle1 = Bundle("Bundle 1", 3, 1.5, conductor1)
    geometry1 = Geometry("Geometry1", 0, 0, 7, 0, 14, 0)

    line1 = TransmissionLine("Line 1", bus1, bus2, bundle1, geometry1, 10)

    print(f"Zpu: {line1.series_impedance:.5f}, Bpu: {line1.shunt_admittance:.5f}")
    print("Yprim Matrix: ")
    # Format and print the Yprim matrix
    yprim_df = pd.DataFrame(line1.calc_yprim())
    print(yprim_df)
