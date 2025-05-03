import numpy as np
from Settings import s

class Generator:
    def __init__(self, name:str,voltage_setpoint:float, mw_setpoint:float):
        self.name = name
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint
        self.sub_trans=None

    def calc_Impedance(self, sub_trans):
        self.sub_trans=complex(0,sub_trans * (s.base_power / self.mw_setpoint))


