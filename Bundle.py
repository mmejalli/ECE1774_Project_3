from Conductor import Conductor

class Bundle:
    def __init__(self, name:str, num_conductors:float, spacing:float, conductor:Conductor):
        self.name = name
        self.num_conductors = num_conductors
        self.spacing = spacing  #units in feet
        self.conductor = conductor
        self.DSC = None #units in feet
        self.DSL = None #units in feet

        self.calc_DSL()
        self.calc_DSC()

    def calc_DSC(self):
        #make sure rad is in feet (divide by 2 to get radius, 12 to get feet)
        rad_ft=self.conductor.diam/24

        #Calculation of DSC changes for number of conductors.
        #See Module 5 conductor bundling
        match self.num_conductors:
            case 1:
                self.DSC=rad_ft
            case 2:
                self.DSC=(rad_ft*self.spacing)**(1/2)
            case 3:
                self.DSC=(rad_ft*self.spacing**2)**(1/3)
            case 4:
                self.DSC=1.091*(rad_ft*self.spacing**3)**(1/4)

    # Calculation of DSC changes for number of conductors.
    # See Module 5 conductor bundling
    def calc_DSL(self):
        match self.num_conductors:
            case 1:
                self.DSL=self.conductor.GMR
            case 2:
                self.DSL=(self.conductor.GMR * self.spacing)**(1/2)
            case 3:
                self.DSL=(self.conductor.GMR * self.spacing**2)**(1/3)
            case 4:
                self.DSL=(self.conductor.GMR * self.spacing**3)**(1/4)





if __name__ == "__main__":

    conductor1=Conductor("Partridge", 0.642,0.0217,0.385,460)
    bundle1=Bundle("Bundle 1", 3, 1.5, conductor1)

    print("DSL: ",bundle1.DSL)
    print("DSC: ",bundle1.DSC)