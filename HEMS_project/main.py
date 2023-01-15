from unschedulable_app import Unschedulable
from interuptible_app import Interuptible
from non_interuptible_app import NonInteruptible

from photovoltaic import PV_cell
from battery import Battery
from household import Household

num_slots = 48

# Configure the Photo-voltaic cell
pv_area = 50.0       # in m2
pv_intensity = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2.5, 7.5, 15.0, 25.0, 35.0, 50.0, 65.0, 80.0, 92.5, 100.0, 100.0, 92.5, 80.0, 65.0, 50.0, 35.0, 25.0, 15.0, 7.5, 2.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]              # in W/m2
pv_power = [pv_area*x/1000.0 for x in pv_intensity]     # in KW
pv_cell = PV_cell(pv_power)

# Configuring the Battery
total_capacity_KWh = 10             # In units
total_capacity_KJ = 10*60*60        # In KJ
charge_efficiency = 2.0             # In KW
discharge_efficiency = 2.0          # In KW
SOC = 0.5
battery = Battery(total_capacity_KJ,charge_efficiency,discharge_efficiency,SOC)

# Configuring the Appliances
app_types = [Unschedulable, Interuptible, NonInteruptible]

names = ["LED Bulb", "Television", "Air conditioner", "Humidifier", "Water heater", "Water Pump", "Dish washer", "Waching machine"]
ids = [0, 0, 0, 1, 1, 1, 2, 2]
slots = [[[12,18],[36,48]], [[16,20],[38,46]], [[0,16],[38,48]] , [[0,18,8],[28,40,8]], [[8,17,6],[32,40,4],[42,48,3]], [[0,16,6],[14,36,8],[32,48,8],[36,48,8]], [[16,24,3],[40,46,3]], [[12,15,2],[30,34,2]]]
powers = [[0.4,0.4], [0.1,0.1], [0.75,0.75], [0.15,0.15], [0.74,0.70,0.64], [1.0,1.8,1.0,1.1], [0.73,0.73], [0.8,0.8]]

allAppliances = []
for i,x in enumerate(zip(names,ids,slots,powers)):
    name,id,slot,power = x
    appliance = app_types[id](name,slot,power)
    allAppliances.append(appliance)

# Configuring Real-time pricing environment
rtp = [225,225,225,225,225,225,225,225,225,225,225,225,425,425,425,425,425,425,425,425,325,325,325,325,325,325,325,325,325,325,325,325,325,325,325,325,425,425,425,425,425,425,425,425,225,225,225,225]   # in paise/unit    
rtp_KJ = [x/(100*60*60) for x in rtp]      # in Rs per KJ

household = Household(allAppliances,battery,pv_cell,rtp_KJ)
household.make_mapping()

schedule = household.random_scheduler()
total_cost = household.simulate(schedule,visualize=True)
print("Total cost in Rs for Random scheduling: ",total_cost)

schedule = household.genetic_scheduler(visualize=True)
total_cost = household.simulate(schedule,visualize=True)
print("Total cost in Rs for Genetic scheduling: ",total_cost)