class PV_cell:
    def __init__(self,harvesting_rate):
        self.harvesting_rate = harvesting_rate

    def get_renewable_energy(self,slot_id):
        return self.harvesting_rate[slot_id]*30*60