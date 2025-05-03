from Powerflow import Powerflow
from Settings import Settings
from Circuit import Circuit

import numpy as np
import pandas as pd

s = Settings()


class Newton_Raphson:
    def __init__(self, circuit: Circuit, tol: float = 0.001, max_iter: int = 50):
        self.circuit = circuit
        self.tol = tol
        self.max_iter = max_iter
        self.buses = circuit.buses
        self.circuit.calc_y_admit()
        self.powerflow = Powerflow(circuit)
        self.powerflow.flat_start()
        self.p_inj,self.q_inj =  self.powerflow.calc_PQ()

    #Function to solve Newton Raphson Method
    def solve(self):

        #Begin from iteration 0 with flat start mismatches
        iteration = 0

        #Continue algorithm until max iterations are reached
        while iteration < self.max_iter:

            #Start with flat start mismatches, compute using p_inj and q_inj
            mismatch = self.powerflow.calc_mismatch(self.p_inj, self.q_inj)

            #if mismatches are within tolerance, algorithm stops
            if np.max(np.abs(mismatch)) < self.tol:
                break

            #Calculate Jacobian Matrix based on mismatches
            jacobian = self.compute_jacobian()

            #Change in x(mismatches) solved via linear algebra
            delta_x = np.linalg.solve(jacobian, mismatch)

            #Update voltage values
            self.update_voltages(delta_x)

            #Move on to next iteration
            iteration += 1

        #Once exiting loop, check if max iterations was reached
        if iteration == self.max_iter:
            print("Warning: Newton-Raphson method did not converge")

    def update_voltages(self, delta_x):
        self.angles[:-1] += delta_x[:len(self.angles) - 1]
        self.voltages[self.pq_buses] += delta_x[len(self.angles) - 1:]