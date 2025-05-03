import numpy as np

class Load:
    def __init__(self, name:str, real_power:float, reactive_power:float):
        self.name = name
        self.real_power = real_power
        self.reactive_power = reactive_power