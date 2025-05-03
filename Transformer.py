import numpy as np
from Bus import Bus
from Settings import s
import math

class Transformer:
    def __init__(self, name: str, bus1: Bus, bus2: Bus, power_rating: float, impedance_percent: float,
                 x_over_r_ratio: float):
        """Initialize a Transformer instance with given parameters."""
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.power_rating = power_rating
        self.impedance_percent = impedance_percent
        self.x_over_r_ratio = x_over_r_ratio

        # Calculate impedance and admittance values
        self.impedance = self.calculate_impedance()
        self.admittance = 1 / self.impedance if self.impedance != 0 else float('inf')
        self.y_prim_mat=None

    def calculate_impedance(self):
        """Calculate the impedance based on power rating and impedance percentage."""
        base_impedance = (self.bus1.base_kv ** 2) / self.power_rating
        system_impedence = (self.bus1.base_kv ** 2) / s.base_power # Change in settings, 100 represents the system power base
        z_pu_mag = ((self.impedance_percent / 100)*base_impedance)/system_impedence
        z_pu_angle=math.atan(self.x_over_r_ratio)
        z_pu=z_pu_mag * complex(math.cos(z_pu_angle), math.sin(z_pu_angle))
        return z_pu

    def calculate_admittance(self):
        """Calculate the admittance as the reciprocal of impedance."""
        return 1 / self.impedance if self.impedance != 0 else float('inf')

    def yprim(self):
        """Compute the primitive admittance matrix."""
        y = self.calculate_admittance()
        self.y_prim_mat=np.array([[y, -y], [-y, y]])
        return self.y_prim_mat

    def Rpu_Xpu(self):
        base_impedance = (self.bus1.base_kv ** 2) / self.power_rating
        z_pu = self.impedance_percent / 100
        x_pu = z_pu * self.x_over_r_ratio/np.sqrt(1+self.x_over_r_ratio**2)
        r_pu = z_pu * 1/np.sqrt(1 + self.x_over_r_ratio**2)
        return r_pu, x_pu

    def __str__(self):
        """Return a formatted string representing the transformer object."""
        return (
            f"Transformer: {self.name}\n"
            f"Connected Buses: {self.bus1.name} <--> {self.bus2.name}\n"
            f"Power Rating: {self.power_rating} MVA\n"
            f"Impedance (%): {self.impedance_percent}%\n"
            f"X/R Ratio: {self.x_over_r_ratio}\n"
            f"Impedance (Ω): {self.impedance:.4f}\n"
            f"Admittance (S): {self.admittance:.6f}\n"
            f"Y-Primitive Matrix: {self.yprim}"
        )

'''
if __name__ == "__main__":
    """
    Transformer Validation
    """
    bus1 = Bus("Bus 1", 20)
    bus2 = Bus("Bus 2", 230)

    transformer1 = Transformer("T1", bus1, bus2, 125, 8.5, 10)

    # Assume 100 mva base
    print("Zpu: ", transformer1.calculate_impedance(), "Ypu: ", transformer1.calculate_admittance())
    print("Yprim Matrix: ")
    # Format and print the Yprim matrix
    yprim_df = pd.DataFrame(transformer1.calc_yprim())
    print(yprim_df)
'''