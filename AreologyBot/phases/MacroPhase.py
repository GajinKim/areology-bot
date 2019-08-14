import functions
from functions.Army import *
from functions.Unit import *
from functions.Build import *
from functions.Train import *

"""""""""""
Priority: Upgrade > Build > Train > Army / Unit
"""""""""""
class HatchTech:
    async def research_upgrades(self):
        # Range / Armor > Melee
        return

    async def build_structures(self):
        await Build.hatch_tech_buildings(self)

    async def train_units(self):
        # Overlords > Queens > Drones > Army
        await Train.train_overlord(self)
        await Train.train_queen(self)
        await Train.train_drone(self) # hatchery count keeps drone production in check
        await Train.hatch_train_army(self) # drone count keeps army production in check

    async def army_control(self):
        await Army.send_army_to_attack(self)
        await Army.send_army_to_defend(self)

    async def unit_micro(self):
        await Unit.micro_units(self)

class LairTech:
    async def research_upgrades(self):
        # Range / Armor > Melee
        return

    async def build_structures(self):
        await Build.hatch_tech_buildings(self)
        await Build.lair_tech_buildings(self)

    async def train_units(self):
        # Overlords > Queens > Drones > Army
        await Train.train_overlord(self)
        await Train.train_queen(self)
        await Train.train_drone(self) # hatchery count keeps drone production in check
        await Train.lair_train_army(self) # drone count keeps army production in check

    async def army_control(self):
        await Army.send_army_to_attack(self)
        await Army.send_army_to_defend(self)

    async def unit_micro(self):
        await Unit.micro_units(self)

class HiveTech:
    async def research_upgrades(self):
        # Range / Armor > Melee
        return

    async def build_structures(self):
        await Build.hatch_tech_buildings(self)
        await Build.lair_tech_buildings(self)
        await Build.hive_tech_buildings(self)

    async def train_units(self):
        # Overlords > Queens > Drones > Army
        await Train.train_overlord(self)
        await Train.train_queen(self)
        await Train.train_drone(self) # hatchery count keeps drone production in check
        await Train.hive_train_army(self) # drone count keeps army production in check

    async def army_control(self):
        await Army.send_army_to_attack(self)
        await Army.send_army_to_defend(self)

    async def unit_micro(self):
        await Unit.micro_units(self)
