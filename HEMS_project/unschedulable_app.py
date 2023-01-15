"""
Unschedulable appliances have to be scheduled in the mentioned slots else the customer satisfaction will drop
"""

class Unschedulable:
    def __init__(self,name,slots,power):
        self.name = name
        self.slots = slots
        self.power = power

    def __str__(self):
        s = f"{self.name} : This an unschedulable load\n"
        for i in range(len(self.slots)):
            s += f"It must operate throughout [{self.slots[i][0]}-{self.slots[i][1]}] with power {self.power[i]}\n"
        return s