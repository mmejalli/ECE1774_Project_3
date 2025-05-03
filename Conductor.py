

class Conductor:
    #diameter is in units of inches
    def __init__(self, name:str, diam:float, GMR:float, resistance:float, ampacity:float):
        self.name = name
        self.diam = diam    #units in inches
        self.GMR = GMR  #Units in feet
        self.resistance = resistance
        self.ampacity = ampacity


if __name__ == "__main__":
    conductor1=Conductor("Partridge", 0.642,0.0217,0.385,460)
    print("Name:",conductor1.name)
    print("Diameter:",conductor1.diam)
    print("GMR:",conductor1.GMR)
    print("Resistance:",conductor1.resistance)
    print("Ampacity:",conductor1.ampacity)