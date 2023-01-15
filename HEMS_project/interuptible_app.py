"""
Non-interuptible appliances have to be scheduled in the given time slot in range [a,b] for c timeslots
"""

class Interuptible:
    def __init__(self,name,slots,power):
        self.name = name
        self.slots = slots
        self.power = power

    def __str__(self):
        s = f"{self.name} : This an interuptible load\n"
        for i in range(len(self.slots)):
            s += f"It must operate for {self.slots[i][2]} slots in [{self.slots[i][0]}-{self.slots[i][1]}] with power {self.power[i]}\n"
        return s