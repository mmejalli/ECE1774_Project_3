import numpy as np
import math
import cmath
import pandas as pd


class Jacobian:
    def __init__(self,circuit):
       self.circuit=circuit
       self.jacobian=None

    def calc_jacobian(self):
        J1=self.calc_J1()
        J2=self.calc_J2()
        J3=self.calc_J3()
        J4=self.calc_J4()

        jacobian=np.block([[J1,J2],[J3,J4]])

        for keys in self.circuit.buses.keys():

            if(self.circuit.buses[keys].bus_type == "Slack_Bus"):
                index_Slack=self.circuit.buses[keys].index
            if(self.circuit.buses[keys].bus_type == "PV_Bus"):
                index_PV=self.circuit.buses[keys].index


        jacobian_trimmed=np.delete(jacobian, [index_Slack, index_Slack+len(self.circuit.buses),index_PV+len(self.circuit.buses)],axis=0)
        jacobian_trimmed=np.delete(jacobian_trimmed, [index_Slack, index_Slack+len(self.circuit.buses),index_PV+len(self.circuit.buses)],axis=1)

        self.jacobian=jacobian_trimmed

        return jacobian_trimmed


    def print_jacobian (self):
        #Slight Change for commit

        jacobain_Trimmed_pd = pd.DataFrame(self.jacobian)
        pd.set_option('display.max_rows', None)  # Show all rows
        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.width', 1000)  # Increase the display width
        pd.set_option('display.float_format', lambda x: f'{x:.5f}')

        return jacobain_Trimmed_pd


    def calc_J1(self):

        J1=np.zeros([len(self.circuit.buses),len(self.circuit.buses)],dtype=float)

        for n in self.circuit.buses.keys():
            for k in self.circuit.buses.keys():
                i=self.circuit.buses[n].index
                j=self.circuit.buses[k].index

                busn=self.circuit.buses[n]
                busk=self.circuit.buses[k]
                #ybus=self.circuit.ybus[j,i]

                if(k==n):
                    for p in (self.circuit.buses.keys()):
                        busn=self.circuit.buses[p]
                        i=busn.index
                        if busn.index!=busk.index:
                            J1[j,j]+= abs(self.circuit.ybus[i,j]) * busn.vpu * math.sin(busk.delta - busn.delta - np.angle(self.circuit.ybus[i,j]))  #Check Radians and degrees for cmath
                    J1[j,j]*=(-busk.vpu)
                else:
                    J1[i,j]=busk.vpu * abs(self.circuit.ybus[i,j]) * busn.vpu *math.sin(busk.delta - busn.delta - np.angle(self.circuit.ybus[i,j]))
        return J1

    def calc_J2(self):

        J2=np.zeros([len(self.circuit.buses),len(self.circuit.buses)])

        for n in self.circuit.buses.keys():
            for k in self.circuit.buses.keys():
                i=self.circuit.buses[n].index
                j=self.circuit.buses[k].index

                busn=self.circuit.buses[n]
                busk=self.circuit.buses[k]
                #ybus=self.circuit.ybus[j,i]

                if(k==n):
                    for p in (self.circuit.buses.keys()):
                        busn=self.circuit.buses[p]
                        i=busn.index
                        J2[j,j]+= abs(self.circuit.ybus[i,j]) * busn.vpu * math.cos(busk.delta - busn.delta - np.angle(self.circuit.ybus[i,j]))
                    J2[j,j]*=(busk.vpu*abs(self.circuit.ybus[j,j])*math.cos(np.angle(self.circuit.ybus[j,j])))
                else:
                    J2[i,j]=busk.vpu * abs(self.circuit.ybus[i,j]) * math.cos(busk.delta - busn.delta - np.angle(self.circuit.ybus[i,j]))
        return J2

    def calc_J3(self):

        J3=np.zeros([len(self.circuit.buses),len(self.circuit.buses)])

        for n in self.circuit.buses.keys():
            for k in self.circuit.buses.keys():
                i=self.circuit.buses[n].index
                j=self.circuit.buses[k].index

                busn=self.circuit.buses[n]
                busk=self.circuit.buses[k]
                #ybus=self.circuit.ybus[j,i]

                if(k==n):
                    for p in (self.circuit.buses.keys()):
                        busn=self.circuit.buses[p]
                        i=busn.index
                        if busn.index!=busk.index:
                            J3[j,j]+= abs(self.circuit.ybus[i,j]) * busn.vpu * math.cos(busk.delta - busn.delta - np.angle(self.circuit.ybus[i,j]))
                    J3[j,j]*=(busk.vpu)
                else:
                    J3[i,j]=(-1)*busk.vpu * abs(self.circuit.ybus[i,j]) * busn.vpu *math.cos(busk.delta - busn.delta - np.angle(self.circuit.ybus[i,j]))
        return J3

    def calc_J4(self):

        J4=np.zeros([len(self.circuit.buses),len(self.circuit.buses)])

        for n in self.circuit.buses.keys():
            for k in self.circuit.buses.keys():
                i=self.circuit.buses[n].index
                j=self.circuit.buses[k].index

                busn=self.circuit.buses[n]
                busk=self.circuit.buses[k]
                #ybus=self.circuit.ybus[j,i]

                if(k==n):
                    for p in (self.circuit.buses.keys()):
                        busn=self.circuit.buses[p]
                        i=busn.index
                        J4[j,j]+= abs(self.circuit.ybus[i,j]) * busn.vpu * math.sin(busk.delta - busn.delta - np.angle(self.circuit.ybus[i,j]))
                    J4[j,j]*=(-busk.vpu* abs(self.circuit.ybus[j,j]) *math.sin(np.angle(self.circuit.ybus[j,j])))
                else:
                    J4[i,j]=busk.vpu * abs(self.circuit.ybus[i,j]) *math.sin(busk.delta - busn.delta - np.angle(self.circuit.ybus[i,j]))

        return J4