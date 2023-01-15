from matplotlib import style
from unschedulable_app import Unschedulable
from interuptible_app import Interuptible
from non_interuptible_app import NonInteruptible

import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Household:
    def __init__(self,appliances,battery,pv_cell,rtp):
        self.num_slots = 48
        self.app_types = [Unschedulable,Interuptible,NonInteruptible]
        self.appliances = appliances
        self.battery = battery
        self.SOC_init = battery.SOC
        self.pv_cell = pv_cell
        self.rtp = rtp
        self.mapping = "NA"

    def make_mapping(self):
        self.mapping = []
        for i,appliance in enumerate(self.appliances):
            if(type(appliance)==self.app_types[0]):
                for j in range(len(appliance.slots)):
                    self.mapping.append((0,(i,j)))
            elif(type(appliance)==self.app_types[1]):
                for j in range(len(appliance.slots)):
                    self.mapping.append((1,(i,j)))
            else:
                for j in range(len(appliance.slots)):
                    self.mapping.append((2,(i,j)))

    def simulate(self,schedule,visualize=False):
        total_cost = 0.0

        unschedulable_load = [0.0 for _ in range(self.num_slots)]
        interuptible_load = [0.0 for _ in range(self.num_slots)]
        non_interuptible_load = [0.0 for _ in range(self.num_slots)]

        grid_deltas = []

        prev_SOC = self.battery.SOC
        battery_delta = []
        battery_SOC = []
        for j in range(self.num_slots):
            # Compute total energy consumption from various appliances
            consumption_energy = 0.0
            for i in range(len(self.mapping)):
                type, pos = self.mapping[i]
                i_, j_ = pos
                if(type==2):
                    _, _, duration = self.appliances[i_].slots[j_]
                    scheduled = False
                    for k in range(j-duration,j):
                        if(schedule[i][k]):
                            scheduled = True
                            break
                    if(scheduled):
                        non_interuptible_load[j] += self.appliances[i_].power[j_]*30.0*60.0
                        consumption_energy += self.appliances[i_].power[j_]*30.0*60.0
                else:
                    if(schedule[i][j]>0.0):
                        if(type==0):
                            unschedulable_load[j] += self.appliances[i_].power[j_]*30.0*60.0
                            consumption_energy += self.appliances[i_].power[j_]*30.0*60.0
                        else:
                            interuptible_load[j] += self.appliances[i_].power[j_]*30.0*60.0
                            consumption_energy += self.appliances[i_].power[j_]*30.0*60.0

            # Renewable energy from PV cell
            harvested_energy = self.pv_cell.get_renewable_energy(j)

            # Compute energy delta & make battery decision
            delta_energy = harvested_energy-consumption_energy
            grid_delta = self.battery.update(delta_energy)
            battery_delta.append(self.battery.SOC-prev_SOC)
            battery_SOC.append(self.battery.SOC)
            prev_SOC = self.battery.SOC

            # Buy or sell from grid based on grid delta
            if(grid_delta<0):
                total_cost -= self.rtp[j]*grid_delta
            else:
                total_cost -= (self.rtp[j]/2)*grid_delta
            grid_deltas.append(-grid_delta)

        if(visualize):
            # Appliances load
            appliance_load = pd.DataFrame({"unschedulable":unschedulable_load,"interuptible":interuptible_load,"non-interuptible":non_interuptible_load})
            appliance_load.plot(kind='bar',stacked=True)
            plt.xlabel('Time-slot')
            plt.ylabel('Power in KWh')
            plt.show()

            # Grid energy exchange
            plt.title("Grid exchange info")
            plt.bar(list(range(self.num_slots)),grid_deltas)
            plt.plot(list(range(self.num_slots)),grid_deltas,'r')
            plt.axhline(0,0,self.num_slots,color='black')
            plt.legend(["Grid exchange","Zero"])
            plt.show()

            # Battery SOC
            plt.title("Battery usage info")
            plt.axhline(self.battery.SOC_min,0,self.num_slots,color='c')
            plt.axhline(self.battery.SOC_max,0,self.num_slots,color='c')
            plt.plot(list(range(self.num_slots)),battery_SOC,'r')
            plt.bar(list(range(self.num_slots)),battery_delta)
            plt.axhline(0,0,self.num_slots,color='black')
            plt.legend(["SOC_min","SOC_max","Battery SOC","Battery delta","Zero"])
            plt.show()

        # Initialize battery for next simulation
        self.battery.SOC = self.SOC_init

        return total_cost

    def random_scheduler(self):
        schedule = [[0 for i in range(self.num_slots)] for j in range(len(self.mapping))]
        for x in range(len(self.mapping)):
            type, pos = self.mapping[x]
            i, j = pos
            if(type==0):
                app = self.appliances[i]
                start, end = app.slots[j]
                for k in range(start,end):
                    schedule[x][k] = 1
            elif(type==1):
                app = self.appliances[i]
                start, end, duration = app.slots[j]
                arr = list(range(start,end))
                random.shuffle(arr)
                for k in range(duration):
                    schedule[x][arr[k]] = 1
            else:
                app = self.appliances[i]
                start, end, duration = app.slots[j]
                k = random.randint(start,end-duration+1)
                schedule[x][k] = 1

        return schedule

    def genetic_scheduler(self,num_generations=100,num_siblings=100,selection_probability=0.1,visualize=False):
        next_gen = int(num_siblings*selection_probability)
        curr_generation = [self.random_scheduler() for _ in range(next_gen)]
        prev_generation = "NA"
        generation_costs = []
        for i_ in range(num_generations):
            prev_generation = curr_generation
            curr_generation = []

            # Mutate variants in prev generation
            curr_mutations = []
            for j_ in range(num_siblings):
                i = 0
                j = 0
                while(i==j):
                    i = random.randint(0,len(prev_generation)-1)
                    j = random.randint(0,len(prev_generation)-1)
                mutant = self.mutate(prev_generation[i],prev_generation[j])
                curr_mutations.append(mutant)
            curr_mutations += prev_generation

            # Evaluate mutations
            costs = []
            for mutant in curr_mutations:
                costs.append(self.simulate(mutant))
            generation_costs.append(sum(costs)/len(costs))

            # Natural selection
            idxs = list(np.argsort(np.array(costs))[:next_gen])
            for i in idxs:
                curr_generation.append(curr_mutations[i])

            if(visualize):
                print(f"Generation-{i_+1}: Best mutation cost -> {self.simulate(curr_generation[0])}")

        if(visualize):
            plt.title("Genetic Algo - Evolution")
            plt.xlabel("Generation no.")
            plt.ylabel("Total cost in Rs/day")
            plt.plot(list(range(len(generation_costs))),generation_costs)
            plt.savefig("./Results/Genetic-learning")
            plt.close()
        
        return curr_generation[0]

    def mutate(self,mutation1,mutation2):
        mutation = []
        for x in range(len(self.mapping)):
            type, pos = self.mapping[x]
            i, j = pos
            if(type==0):
                mutation.append(mutation1[x])
            elif(type==1):
                row = []
                row1 = mutation1[x]
                row2 = mutation2[x]
                idxs = []
                for i_ in range(self.num_slots):
                    if(row1[i_]+row2[i_]==1):
                        idxs.append(i_)
                random.shuffle(idxs)
                idxs = idxs[:len(idxs)//2]
                for i_,(x1,x2) in enumerate(zip(row1,row2)):
                    if(x1+x2>0):
                        if(x1>0 and x2>0):
                            row.append(1)
                        else:
                            if i_ in idxs:
                                row.append(1)
                            else:
                                row.append(0)
                    else:
                        row.append(0)

                p = random.random()
                if(p<0.5):
                    # Mutate
                    app = self.appliances[i]
                    start, end, duration = app.slots[j]
                    numSwaps = 1
                    for _ in range(numSwaps):
                        i_ = random.randint(start,end-1)
                        j_ = random.randint(start,end-1)
                        temp = row[i_]
                        row[i_] = row[j_]
                        row[j_] = temp
                mutation.append(row)
            else:
                sample = random.random()
                if(sample<0.5):
                    mutation.append(mutation1[x])
                else:
                    mutation.append(mutation2[x])
        return mutation
        