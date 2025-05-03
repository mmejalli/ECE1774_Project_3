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
from circuit import Circuit
from Jacobian import Jacobian
from Symmetrical_Faults import Fault
from Powerflow import Powerflow

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class PowerSystemGUI2:
    def __init__(self, master, circuit, bus_fault:str=None):
        self.master = master
        self.circuit = circuit
        self.bus_fault=bus_fault
        master.title("Power System Simulator")

        # Create a main frame
        main_frame = ttk.Frame(master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create Treeview for hierarchical equipment menu
        self.tree = ttk.Treeview(main_frame)
        self.tree.heading("#0", text="Case Information", anchor="w")


        equipment_node=self.tree.insert("","end",text="Equipment",open=True)
        bus_node=self.tree.insert(equipment_node,"end",text="Buses", open=True)
        gen_node = self.tree.insert(equipment_node, "end", text="Generators", open=True)
        trans_node = self.tree.insert(equipment_node, "end", text="Transformers", open=True)
        load_node = self.tree.insert(equipment_node, "end", text="Loads", open=True)
        lines_node=self.tree.insert(equipment_node, "end", text="Lines", open=True)

        solution_node=self.tree.insert("", "end", text="Solution Details", open=True)
        y_bus_node=self.tree.insert(solution_node, "end", text="Y_Bus", open=True)
        jacobian_node=self.tree.insert(solution_node, "end", text="Jacobian", open=True)
        powerFlow_node=self.tree.insert(solution_node, "end", text="Power Flow", open=True)

        fault_node=self.tree.insert("","end",text="Fault Study",open=True)
        z_bus_node=self.tree.insert(fault_node, "end", text="Z_Bus", open=True)
        ybus_fault=self.tree.insert(fault_node, "end", text="Ybus_Fault", open=True)
        fault_voltages=self.tree.insert(fault_node, "end", text="Fault Voltages", open=True)
        fault_currents=self.tree.insert(fault_node, "end", text="Fault Current", open=True)

        # Add Treeview to the window
        self.tree.pack(side=tk.LEFT, fill=tk.Y)

        # Info display area for detailed equipment info (separate area for data)
        self.info_frame = ttk.Frame(main_frame)
        self.info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


        # Info display area
        self.info_text = tk.Text(main_frame, width=10)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a new Treeview for displaying detailed data (e.g., buses)
        self.data_tree = ttk.Treeview(self.info_frame)
        self.data_tree.pack(fill=tk.BOTH, expand=True)

        # Bind tree item selection
        self.tree.bind("<<TreeviewSelect>>", self.show_equipment_info)

    def show_equipment_info(self, event):
        selected_item = self.tree.selection()[0]
        item_text = self.tree.item(selected_item, "text")



        # Clear previous info
        self.info_text.delete(1.0, tk.END)
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)

        # Try to get info using circuit.get_case_info()
        if(item_text == "Y_Bus"):
            self.circuit.calc_y_admit()
            df=self.circuit.print_ybus()
            self.display_dataframe(df)
        elif(item_text == "Z_Bus"):
            self.circuit.calc_y_admit()
            f=Fault(self.circuit, self.bus_fault)
            f.calc_fault()
            df=f.print_zbus()
            self.display_dataframe(df)
        elif(item_text == "Ybus_Fault"):
            self.circuit.calc_y_admit()
            f = Fault(self.circuit, self.bus_fault)
            f.calc_fault()
            y= f.print_ybus()
            self.display_dataframe(y)
        elif (item_text == "Fault Voltages"):
            self.circuit.calc_y_admit()
            f = Fault(self.circuit, self.bus_fault)
            f.calc_fault()
            volt=f.print_fault_voltages()
            self.display_dataframe(volt)
        elif(item_text == "Jacobian"):
            self.circuit.calc_y_admit()
            J=Jacobian(self.circuit)
            J.calc_jacobian()
            jac=J.print_jacobian()
            self.display_dataframe(jac)
        elif(item_text == "Power Flow"):
            self.circuit.calc_y_admit()
            pf=Powerflow(self.circuit)
            p_mis, q_mis, resultdf=pf.calc_PQ()
            _,_,mismatchdf=pf.calc_mismatch(p_mis, q_mis)
            combined_df=pd.concat([resultdf, mismatchdf])
            self.display_dataframe(combined_df)
        elif(item_text == "Fault Current"):
            self.circuit.calc_y_admit()
            f = Fault(self.circuit, self.bus_fault)
            f.calc_fault()
            current=abs(f.get_faultCurrent())

            self.data_tree["columns"] = "columns"
            self.data_tree["show"] = "headings"
            self.data_tree.insert("","end",values=current)
        else:
            data, columns = self.circuit.get_case_info(item_text)
            self.display(data, columns)

    def display(self, data, columns):

        self.data_tree["columns"] = columns
        self.data_tree["show"] = "headings"

        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=50, anchor="center")

        # Insert rows
        for row in data:
            formatted_row = [f"{x:.5f}" if isinstance(x, float) else x for x in row]
            formatted_row= [f"{x.real:.5f}{x.imag:+.5f}j" if isinstance(x,complex) else x for x in formatted_row]
            self.data_tree.insert("", "end", values=formatted_row)





    def display_dataframe(self, df: pd.DataFrame):
        # Clear previous rows
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)

        # Include index as the first column
        columns = ["Index"] + list(df.columns)
        self.data_tree["columns"] = columns
        self.data_tree["show"] = "headings"

        # Set headings and column properties
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, anchor="center", width=80)

        # Insert rows with index included
        for index, row in df.iterrows():
            formatted_row = [
                                index
                            ] + [
                                f"{val.real:.5f}{val.imag:+.5f}j" if isinstance(val, complex)
                                else f"{val:.5f}" if isinstance(val, float)
                                else str(val)
                                for val in row
                            ]
            self.data_tree.insert("", "end", values=formatted_row)
