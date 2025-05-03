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

import math
import cmath
from Jacobian import Jacobian

class Circuit:
    def __init__(self, name:str):
        self.name = name
        self.transformers={}
        self.buses={}
        self.transmission_lines={}
        self.conductors={}
        self.geometry={}
        self.bundles={}
        self.generators={}
        self.loads={}
        self.ybus=None

    def add_bus(self, name:str, base_kv:float, vpu:float=1, delta:float=0, bus_type:str="PQ_Bus"):

        #Checking Dictionary for duplicate buses
        if name in self.buses:
            print("Error: Bus ",name," already exists")
            return

        #Adding Bus to dictionary
        self.buses[name]=Bus(name, base_kv,vpu,delta,bus_type)


    def add_transformer(self, name:str, bus1:str, bus2:str, power_rating:float, impedance_percent:float, x_over_r_ratio:float):

        #Checking is buses to connect to transformer already exist
        if bus1 not in self.buses or bus2 not in self.buses:
            print("Error: One or both buses does not exist for Transformer",name)
            return

        #Checking for Duplicate Transformers
        if name in self.transformers:
            print("Error: Transformer ",name," already exists")
            return

        #Adding Transformer to Dictionary
        self.transformers[name]=Transformer(name, self.buses[bus1], self.buses[bus2], power_rating,impedance_percent, x_over_r_ratio)

    def add_transmission_lines(self, name:str, bus1:str, bus2:str, bundle:Bundle, geometry:Geometry, length:float):

        #Checking if busses to connect to Transmission Line already exist
        if bus1 not in self.buses or bus2 not in self.buses:
            print("Error: One or both buses does not exist for Transmission Line", name)
            return

        #Checking for Duplicate Transmission Lines
        if name in self.transmission_lines:
            print("Error: Transmission Line ",name," already exists")
            return

        #Adding Transmission Line to Dictionary
        self.transmission_lines[name]=TransmissionLine(name, self.buses[bus1], self.buses[bus2], bundle, geometry, length)

    def add_conductor(self, name:str, diam:float,GRM:float, resistance:float, ampacity:float):
        self.conductors[name]=Conductor(name, diam, GRM, resistance, ampacity)

    def add_bundle(self,name:str, num_conductors:float, spacing:float, conductor:Conductor):
        self.bundles[name]=Bundle(name, num_conductors, spacing, conductor)

    def add_geometry(self, name:str, xa:float, ya:float, xb:float, yb:float, xc:float, yc:float):
        self.geometry[name]=Geometry(name,xa,ya,xb,yb,xc,yc)

    def add_generator(self, name:str, voltage_setpoint:float, mw_setpoint:float, gen_bus_name:str, sub_trans:float):
        if(self.buses[gen_bus_name].bus_type == "PV_Bus" or self.buses[gen_bus_name].bus_type == "Slack_Bus"):
            self.generators[name] = Generator(name, voltage_setpoint, mw_setpoint)
            self.generators[name].calc_Impedance(sub_trans)
            self.buses[gen_bus_name].generator = self.generators[name]
        else:
            print("Error: ",gen_bus_name," is not a valid Bus to add generator")

    def add_load(self, name:str, real_power:float, reactive_power:float, load_bus_name:str):
        if(self.buses[load_bus_name].bus_type == "PQ_Bus"):
            self.loads[name] = Load(name, real_power, reactive_power)
            self.buses[load_bus_name].load = self.loads[name]
        else:
            print("Error: ",load_bus_name," is not a valid PQ Bus")

    def calc_y_admit(self):
        n=len(self.buses)

        y_admit=np.zeros((n,n),dtype=complex)

        for key in self.transformers.keys():

            #Finding Connected buses
            busIn=self.transformers[key].bus1
            busOut=self.transformers[key].bus2

            #Storing Transformer instance yprim matrix
            temp=self.transformers[key].yprim()

            #Placeholders for bus indicies
            i=busIn.index
            j=busOut.index

            #y_admit[i:j+1,i:j+1]=y_admit[i:j+1,i:j+1] + self.transformers[key].y_prim_mat

            #Moving y-prim values into y-admit matrix
            y_admit[i, i] = y_admit[i, i] + temp[0, 0]
            y_admit[i, j] = y_admit[i, j] + temp[0, 1]
            y_admit[j, i] = y_admit[j, i] + temp[1, 0]
            y_admit[j, j] = y_admit[j, j] + temp[1, 1]


        for key in self.transmission_lines.keys():

            busIn=self.transmission_lines[key].bus1
            busOut=self.transmission_lines[key].bus2
            i=busIn.index
            j=busOut.index

            temp=self.transmission_lines[key].calc_yprim()

            #y_admit[i:j,i:j]=y_admit[i:j,i:j] + self.transmission_lines[key].y_prim_mat
            y_admit[i, i] = y_admit[i,i] + temp[0, 0]
            y_admit[i, j] = y_admit[i,j] + temp[0, 1]
            y_admit[j, i] = y_admit[j,i] + temp[1, 0]
            y_admit[j, j] = y_admit[j,j] + temp[1, 1]



        self.ybus=y_admit

    def print_ybus(self):
        bus_names = list(self.buses.keys())
        y_admit_df = pd.DataFrame(self.ybus, index=bus_names, columns=bus_names)

        pd.set_option('display.max_rows', None)  # Show all rows
        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.width', 1000)  # Increase the display width
        pd.set_option('display.float_format', lambda x: f'{x.real:.5f}{x.imag:+.5f}j')
        # Print the DataFrame
        return y_admit_df

    def get_case_info(self, category):
        if category == "Buses":
            columns = ["Bus", "Base KV", "Volts PU", "Voltage Angle", "Generator On Bus", "Load on Bus"]
            data = [(self.buses[bus].name, self.buses[bus].base_kv, self.buses[bus].vpu, self.buses[bus].delta, self.buses[bus].generator.name, self.buses[bus].load.name) for bus in self.buses]
        elif category == "Generators":
            columns = ["Name", "Voltage Setpoint", "MW Setpoint", "X0"]
            data = [(self.generators[gen].name, self.generators[gen].voltage_setpoint, self.generators[gen].mw_setpoint, abs(self.generators[gen].sub_trans)) for gen in self.generators]
        elif category == "Lines":
            columns = ["From", "To", "Series Resistance (R)", "Series Reactance (X)","Shunt Charging (B)" ,"Length","Conductor Type"]
            data = [(self.transmission_lines[line].bus1.name, self.transmission_lines[line].bus2.name, self.transmission_lines[line].series_impedance.real, self.transmission_lines[line].series_impedance.imag,self.transmission_lines[line].shunt_admittance.imag, self.transmission_lines[line].length, self.transmission_lines[line].bundle.conductor.name) for line in self.transmission_lines]
        elif category == "Transformers":
           columns=["Name","Bus1","Bus2", "Primary Volt","Secondary Volt","Power Rating","PU Impedance"]
           data=[(self.transformers[tran].name,self.transformers[tran].bus1.name, self.transformers[tran].bus2.name, self.transformers[tran].bus1.base_kv, self.transformers[tran].bus2.base_kv, self.transformers[tran].power_rating, self.transformers[tran].impedance )for tran in self.transformers]
        elif category == "Loads":
            columns=["Name", "Real Power (W)", "Reactive Power (var)"]
            data=[(self.loads[load].name, self.loads[load].real_power, self.loads[load].reactive_power) for load in self.loads]
        else:
            columns = []
            data = []

        return data, columns



if __name__ == "__main__":

    circuit1=Circuit("Circuit1")

    #Adding buses
    circuit1.add_bus("bus1",20,bus_type="Slack_Bus")
    circuit1.add_bus("bus2",230)
    circuit1.add_bus("bus3",230)
    circuit1.add_bus("bus4",230)
    circuit1.add_bus("bus5",230)
    circuit1.add_bus("bus6",230)
    circuit1.add_bus("bus7",18,bus_type="PV_Bus")

    #Transmission Line sub-classes
    conductor1=Conductor("Partridge",0.642,0.0217,0.385,460)
    bundle1=Bundle("Bundle1",2,1.5,conductor1)
    geometry1=Geometry("Geometry1",0,0,9.75*2,0,9.75*4,0)

    #Adding Transmission Lines
    circuit1.add_transmission_lines("Line1","bus2","bus4",bundle1,geometry1,10)
    circuit1.add_transmission_lines("line2","bus2","bus3",bundle1,geometry1,25)
    circuit1.add_transmission_lines("line3","bus3","bus5",bundle1,geometry1,20)
    circuit1.add_transmission_lines("Line4","bus4","bus6",bundle1,geometry1,20)
    circuit1.add_transmission_lines("Line5","bus5","bus6",bundle1,geometry1,10)
    circuit1.add_transmission_lines("Line6","bus4","bus5",bundle1,geometry1,35)

    #Adding Transformers
    circuit1.add_transformer("Tx1","bus1","bus2",125,8.5,10)
    circuit1.add_transformer("Tx2","bus6","bus7",200,10.5,12)

    # Adding Generators
    circuit1.add_generator("Gen1", 20, 100, "bus1", 0.12)
    circuit1.add_generator("Gen2", 18, 100, "bus7", 0.12)

    # Adding Loads
    circuit1.add_load("Load1", 0, 0, "bus2")
    circuit1.add_load("Load2", 110, 50, "bus3")
    circuit1.add_load("Load3", 100, 70, "bus4")
    circuit1.add_load("Load4", 100, 65, "bus5")
    circuit1.add_load("Load5", 0, 0, "bus6")

    #Calculate y_bus
    circuit1.calc_y_admit()

    #Calc Jacobian
    J=Jacobian(circuit1)
    J.calc_jacobian()

    #Newton Raphson Initialization
    solver=Newton_Raphson(circuit1)

    #Symmetrical Fault Calculations
    fault1 = Fault(circuit1, "bus7")
    fault1.calc_fault()
    fault1.print_zbus()
    fault1.print_fault_voltages()


    ''' 
    #Testing Attribute Initialization
    circuit1=Circuit("Test Circuit")
    circuit1.add_bus("Bus1", 230)
    circuit1.add_bus("Bus2", 13)
    circuit1.add_transformer("Tx1","Bus1","Bus2",100, 3, .8)

    print(circuit1.name)
    print(type(circuit1.name))
    print(circuit1.buses)
    print(circuit1.transformers)
    print(circuit1.transmission_lines)
    print(type(circuit1.buses))
    print(type(circuit1.transformers))
    print(type(circuit1.transmission_lines))
    print(type(circuit1.buses["Bus1"]))
    print(circuit1.buses["Bus1"].name,circuit1.buses["Bus1"].base_kv)
    #print(circuit1.transformers["Tx1"].name,type(circuit1.transformers["Tx1"]),circuit1.transformers["Tx1"].bus1.name,type(circuit1.transformers["Tx1"].bus1))
    '''
    ''' 
    #Testing Bus Existence
    circuit2=Circuit("Test Circuit 2")

    circuit2.add_bus("Bus1", 230)
    circuit2.add_bus("Bus2", 13)

    print(circuit2.buses)

    circuit2.add_transformer("Tx1","Bus1","Bi",100, 3, .8)
    circuit2.add_transmission_lines("TL1","Bus1","Bi",None, None, .8)


    #Testing Redundancy
    circuit3=Circuit("Test Circuit 3")
    circuit3.add_bus("Bus1", 230)
    circuit3.add_bus("Bus1", 230)

    circuit3.add_bus("Bus2", 13)

    circuit3.add_transformer("Tx1","Bus1","Bus1",100, 3, .8)
    circuit3.add_transformer("Tx1","Bus1","Bus2",100, 3, .8)

    circuit3.add_transmission_lines("TL1","Bus1","Bus2",None, None, .8)
    circuit3.add_transmission_lines("TL1","Bus1","Bus2",None, None, .8)
    '''

    #Testing Power System
    '''
    circuit4=Circuit("Test Circuit 4")

    circuit4.add_bus("Bus1", 13)
    circuit4.add_bus("Bus2", 230)
    circuit4.add_bus("Bus3",230)
    circuit4.add_bus("Bus4", 230)
    circuit4.add_bus("Bus5", 230)
    circuit4.add_bus("Bus6", 230)
    circuit4.add_bus("Bus7", 130)

    conductor1=Conductor("Test Conductor", 12, 3, 4, 1)
    geometry1=Geometry("Test Geometry", 2,3,5,1,3,2)
    Bundle1=Bundle("Bundle1",3,4,conductor1)

    circuit4.add_transformer("Tx1","Bus1","Bus2", 100, 3, .8)
    circuit4.add_transformer("Tx2","Bus6","Bus7", 100, 3, .8)

    circuit4.add_transmission_lines("TL1","Bus2","Bus4", Bundle1, geometry1, 10)
    circuit4.add_transmission_lines("TL2","Bus2","Bus3", Bundle1, geometry1, 10)
    circuit4.add_transmission_lines("TL3","Bus3","Bus6", Bundle1, geometry1, 10)
    circuit4.add_transmission_lines("TL4","Bus4","Bus6", Bundle1, geometry1, 10)
    circuit4.add_transmission_lines("TL5","Bus5","Bus6", Bundle1, geometry1, 10)
    circuit4.add_transmission_lines("TL6","Bus4","Bus5", Bundle1, geometry1, 10)

    for bus in circuit4.buses:
        print(circuit4.buses[bus].name, circuit4.buses[bus].base_kv)

    for transformer in circuit4.transformers:
        print(circuit4.transformers[transformer].name, circuit4.transformers[transformer].bus1.name, circuit4.transformers[transformer].bus2.name)

    for transmission_line in circuit4.transmission_lines:
        print(circuit4.transmission_lines[transmission_line].name, circuit4.transmission_lines[transmission_line].bus1.name, circuit4.transmission_lines[transmission_line].bus2.name)
'''



