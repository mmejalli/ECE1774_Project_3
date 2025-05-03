import numpy as np

class Geometry:
    def __init__(self, name:str, xa:float, ya:float, xb:float, yb:float, xc:float, yc:float):
        self.name = name
        self.xa = xa
        self.ya = ya
        self.xb = xb
        self.yb = yb
        self.xc = xc
        self.yc = yc
        self.DEQ=None

        self.calcDEQ()

    def calcDEQ(self):
        dAB=(((self.xa-self.xb)**2+(self.ya-self.yb)**2))**(1/2)
        dAC=(((self.xa-self.xc)**2)+((self.ya-self.yc)**2))**(1/2)
        dBC=(((self.xb-self.xc)**2)+((self.yb-self.yc)**2))**(1/2)

        self.DEQ=(dAB*dAC*dBC)**(1/3)

if __name__=='__main__':
    geo1=Geometry("Geometry1",0,0,7,0,14,0)
    print("DEQ=",geo1.DEQ)
