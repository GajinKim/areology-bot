import functions
from functions.Army import *
from functions.Unit import *
from functions.Build import *
from functions.Train import *

"""""""""""
Priority: Upgrade > Build > Train > Army / Unit
"""""""""""
class MidGame:
    async def research_upgrades(self):
        return

    async def build_structures(self):
        await Build.hatch_tech_buildings(self)
        await Build.lair_tech_buildings(self)

    async def train_units(self):
        await Train.train_drone(self)
        await Train.train_overlord(self)
        await Train.train_queen(self)
        await Train.mg_train_army(self)

    async def army_control(self):
        await Army.send_army_to_attack(self)
        await Army.send_army_to_defend(self)

    async def unit_micro(self):
        await Unit.micro_units(self)
