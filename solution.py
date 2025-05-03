import numpy as np
import pandas as pd
from Bus import Bus
from Geometry import Geometry
from Conductor import Conductor
from Transformer import Transformer
from Bundle import Bundle
from TransmissionLine import TransmissionLine
from Geometry import Geometry
from Load import Load
from Generator import Generator
from circuit import Circuit
from Jacobian import Jacobian
from Symmetrical_Faults import Fault
from User_Interface import PowerSystemGUI
import tkinter as tk
from GUI2 import PowerSystemGUI2


circuit1 = Circuit("Circuit1")

# Adding buses
circuit1.add_bus("bus1", 20, bus_type="Slack_Bus")
circuit1.add_bus("bus2", 230)
circuit1.add_bus("bus3", 230)
circuit1.add_bus("bus4", 230)
circuit1.add_bus("bus5", 230)
circuit1.add_bus("bus6", 230)
circuit1.add_bus("bus7", 18, bus_type="PV_Bus")

# Transmission Line sub-classes
conductor1 = Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
bundle1 = Bundle("Bundle1", 2, 1.5, conductor1)
geometry1 = Geometry("Geometry1", 0, 0, 9.75 * 2, 0, 9.75 * 4, 0)

# Adding Transmission Lines
circuit1.add_transmission_lines("Line1", "bus2", "bus4", bundle1, geometry1, 10)
circuit1.add_transmission_lines("line2", "bus2", "bus3", bundle1, geometry1, 25)
circuit1.add_transmission_lines("line3", "bus3", "bus5", bundle1, geometry1, 20)
circuit1.add_transmission_lines("Line4", "bus4", "bus6", bundle1, geometry1, 20)
circuit1.add_transmission_lines("Line5", "bus5", "bus6", bundle1, geometry1, 10)
circuit1.add_transmission_lines("Line6", "bus4", "bus5", bundle1, geometry1, 35)

# Adding Transformers
circuit1.add_transformer("Tx1", "bus1", "bus2", 125, 8.5, 10)
circuit1.add_transformer("Tx2", "bus6", "bus7", 200, 10.5, 12)

#Adding Generators
circuit1.add_generator("Gen1", 20, 100, "bus1", 0.12)
circuit1.add_generator("Gen2", 18, 100, "bus7", 0.12)

# Adding Loads
circuit1.add_load("Load1", 0, 0, "bus2")
circuit1.add_load("Load2", 110, 50, "bus3")
circuit1.add_load("Load3", 100, 70, "bus4")
circuit1.add_load("Load4", 100, 65, "bus5")
circuit1.add_load("Load5", 0, 0, "bus6")


root = tk.Tk()
power = PowerSystemGUI2(root, circuit1,"bus1")
root.mainloop()