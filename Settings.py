

class Settings:
    def __init__(self, frequency:float=60, base_power:float=100):
        self.frequency = frequency  #Value in Hz
        self.base_power = base_power    #Value in MVA

    def get_frequency(self):
        return self.frequency

    def get_base_power(self):
        return self.base_power

s=Settings()