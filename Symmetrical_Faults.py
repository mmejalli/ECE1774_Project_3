import numpy as np
from circuit import Circuit
from Bus import Bus
from Conductor import Conductor
from Bundle import Bundle
from Geometry import Geometry
import pandas as pd

class Fault:

    def __init__(self, circuit:Circuit,bus_fault):
        self.circuit = circuit
        self.bus_fault = circuit.buses[bus_fault]
        self.zbus=None
        self.fault_current=None
        self.fault_voltages=None


    def calc_fault(self):

        y_bus=self.circuit.ybus


        for bus in self.circuit.buses.keys():
            if(self.circuit.buses[bus].bus_type == "PV_Bus"):
                pv_index=self.circuit.buses[bus].index
            elif (self.circuit.buses[bus].bus_type == "Slack_Bus"):
                slack_index=self.circuit.buses[bus].index

        pv_bus_name=f"bus{pv_index+1}"
        slack_bus_name=f"bus{slack_index+1}"

        gen_pv=self.circuit.buses[pv_bus_name].generator
        gen_slack=self.circuit.buses[slack_bus_name].generator

        y_bus[pv_index,pv_index]+= (gen_pv.sub_trans)**(-1)
        #y_bus[pv_index-1,pv_index]+= (gen_pv.sub_trans)**(-1)
        #y_bus[pv_index,pv_index-1]+= (gen_pv.sub_trans)**(-1)


        y_bus[slack_index,slack_index]+= (gen_slack.sub_trans)**(-1)
        #y_bus[slack_index+1,slack_index]+= (gen_slack.sub_trans)**(-1)
        #y_bus[slack_index,slack_index+1]+= (gen_slack.sub_trans)**(-1)



        self.circuit.ybus=y_bus
        z_bus=np.zeros_like(y_bus)

        z_bus=np.linalg.inv(y_bus)
        #z_bus=np.linalg.inv(z_bus)

        self.zbus=z_bus

        for bus in self.circuit.buses:
            self.circuit.buses[bus].vpu=1

        n=self.bus_fault.index
        self.fault_current=self.bus_fault.vpu/z_bus[n,n]

        self.fault_voltages=np.zeros((1,len(self.circuit.buses)),dtype=complex)
        for bus in self.circuit.buses:
            k=self.circuit.buses[bus].index

            zkn=z_bus[k,n]
            znn=z_bus[n,n]
            Vf=self.circuit.buses[bus].vpu
            faultVoltage=(1-(zkn/znn))*Vf
            self.fault_voltages[0,k]=(1-(zkn/znn))*Vf




    def print_fault_voltages(self):
        bus_names = list(self.circuit.buses.keys())

        faultVoltages=abs(self.fault_voltages)

        volt = pd.DataFrame(faultVoltages,index=["Fault Voltages (PU)"], columns=bus_names)

        pd.set_option('display.max_rows', None)  # Show all rows
        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.width', 1000)  # Increase the display width
        pd.set_option('display.float_format', lambda x: f'{x.real:.5f}')
        # Print the DataFrame
        print("\n",volt)
        print("Fault current at "+self.bus_fault.name+" is", abs(self.fault_current))
        return volt


    def print_zbus(self):
        bus_names = list(self.circuit.buses.keys())

        z_busdf = pd.DataFrame(self.zbus, index=bus_names, columns=bus_names)

        pd.set_option('display.max_rows', None)  # Show all rows
        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.width', 1000)  # Increase the display width
        pd.set_option('display.float_format', lambda x: f'{x.real:.5f}{x.imag:+.5f}j')
        # Print the DataFrame
        print(z_busdf)
        return z_busdf

    def print_ybus(self):
        bus_names = list(self.circuit.buses.keys())
        y_bus=np.linalg.inv(self.zbus)
        y_busdf = pd.DataFrame(y_bus, index=bus_names, columns=bus_names)

        pd.set_option('display.max_rows', None)  # Show all rows
        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.width', 1000)  # Increase the display width
        pd.set_option('display.float_format', lambda x: f'{x.real:.5f}{x.imag:+.5f}j')
        # Print the DataFrame
        print(y_busdf)
        return y_busdf



    def get_faultCurrent(self):
        return self.fault_current

if __name__ == "__main__":
    circuit1 = Circuit("Circuit1")

    # Adding buses
    circuit1.add_bus("bus1", 20, bus_type="Slack_Bus")
    circuit1.add_bus("bus2", 230)
    circuit1.add_bus("bus3", 230)
    circuit1.add_bus("bus4", 230)
    circuit1.add_bus("bus5", 230)
    circuit1.add_bus("bus6", 230)
    circuit1.add_bus("bus7", 18,bus_type="PV_Bus")

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

    circuit1.add_generator("Gen1",20, 100,"bus1",0.12)
    circuit1.add_generator("Gen2",18, 100,"bus7",0.12)
    circuit1.calc_y_admit()
    circuit1.print_ybus()

    fault1=Fault(circuit1,"bus1")
    fault1.calc_fault()
    fault1.print_zbus()
    fault1.print_ybus()
    fault1.print_fault_voltages()
