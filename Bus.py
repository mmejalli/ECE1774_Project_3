from Load import Load
from Generator import Generator

class Bus:


    bus_count = 0

    #Recently refactored
    def __init__(self, name:str, base_kv:float, vpu:float=1, delta:float=0, bus_type:str="PQ_Bus"):
        """
        Initialize a Bus object.

        :param name: Name of the bus (str).
        :param base_kv: Base KV (float).
        """
        self.name = name
        self.base_kv = base_kv
        self.index = Bus.bus_count
        self.vpu = vpu
        self.delta = delta
        self.generator = Generator("", 0, 0)
        self.load = Load("", 0, 0)

        if bus_type =="Slack_Bus" or bus_type =="PQ_Bus" or bus_type =="PV_Bus":
            self.bus_type = bus_type
        else:
            print("Invalid bus type")

        Bus.bus_count += 1



    def __str__(self):
        """Return a formatted string representing the bus object."""
        return (
            f"Bus Name: {self.name}\n"
            f"Bus Index: {self.index}\n"
            f"Base Voltage: {self.base_kv} kV"
        )

if __name__ == "__main__":
    """
    Bus Validation
    """
    bus1 = Bus("Bus 1", 20)
    bus2 = Bus("Bus 2", 230)

    print(bus1)
    print(bus2)
    print("\nBus count: ", Bus.bus_count)