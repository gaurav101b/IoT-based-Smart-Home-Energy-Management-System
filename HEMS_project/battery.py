class Battery:
    def __init__(self,total_capacity,charge_efficiency,discharge_efficiency,SOC):
        self.total_capacity = total_capacity
        self.charge_efficiency = charge_efficiency
        self.discharge_efficiency = discharge_efficiency

        self.SOC = SOC
        self.SOC_min = 0.1
        self.SOC_max = 0.9

    def update(self,delta_energy):
        # positive delta indicates surplus
        if(delta_energy>0.0):
            Bcc = (self.SOC_max - self.SOC)*self.total_capacity
            Bce = self.charge_efficiency*30*60
            if(Bcc<Bce):
                if(delta_energy>Bcc):
                    self.SOC = self.SOC_max
                    return delta_energy-Bcc
                else:
                    self.SOC += delta_energy/self.total_capacity
                    return 0.0
            else:
                if(delta_energy>Bce):
                    self.SOC = self.SOC_max
                    return delta_energy-Bce
                else:
                    self.SOC += delta_energy/self.total_capacity
                    return 0.0
        else:
            delta_energy *= -1
            Bdc = (self.SOC - self.SOC_min)*self.total_capacity
            Bde = self.discharge_efficiency*30*60
            if(Bdc<Bde):
                if(delta_energy>Bdc):
                    self.SOC = self.SOC_min
                    return -(delta_energy-Bdc)
                else:
                    self.SOC -= delta_energy/self.total_capacity
                    return 0.0
            else:
                if(delta_energy>Bde):
                    self.SOC = self.SOC_min
                    return -(delta_energy-Bde)
                else:
                    self.SOC -= delta_energy/self.total_capacity
                    return 0.0
