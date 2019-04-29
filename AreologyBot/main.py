import itertools, random, math

import sc2, attack, build, micro, train, unit
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import Point2

from attack.attack_force import *
from build.build_order import *
# from build.build_buildings import *

from train.train_units import *

from unit.drone_attributes import *
from unit.queen_attributes import *

from my_vars import *

# from attributes.queen_injects import inject

class AreologyBot(sc2.BotAI):
    def __init__(self):
        # list of actions we do at each step
        self.actions = []
        # set of things that come from a larva
        self.from_larva = {UnitID.DRONE, UnitID.OVERLORD, UnitID.ZERGLING, UnitID.ROACH}
        # set of things that come from a drone
        self.from_drone = {UnitID.HATCHERY, UnitID.SPAWNINGPOOL, UnitID.EXTRACTOR, UnitID.ROACHWARREN, UnitID.EVOLUTIONCHAMBER, UnitID.SPIRE}
        # buildorder
        self.buildorder = [
            UnitID.DRONE,       # 13/14
            UnitID.OVERLORD,    # 13/14
            UnitID.DRONE,       # 14/14
            UnitID.DRONE,       # 15/22
            UnitID.DRONE,       # 16/22
            UnitID.DRONE,       # 17/22
            UnitID.HATCHERY,    # 16/22
            UnitID.DRONE,       # 17/22
            UnitID.DRONE,       # 18/22
            UnitID.EXTRACTOR,   # 17/22
            UnitID.SPAWNINGPOOL,# 16/22
            UnitID.DRONE,       # 17/22
            UnitID.DRONE,       # 18/22
            UnitID.DRONE,       # 19/22
            UnitID.OVERLORD,    # 19/22
            UnitID.DRONE,       # 20/22
            UnitID.QUEEN,       # 22
            UnitID.QUEEN,       # 24
            UnitID.ZERGLING,    # 25
            UnitID.ZERGLING,    # 26
            AbilID.RESEARCH_ZERGLINGMETABOLICBOOST, # 26
            UnitID.ROACHWARREN, # 25
            UnitID.DRONE,       # 26
            UnitID.DRONE,       # 27
            UnitID.DRONE,       # 28
            UnitID.DRONE,       # 29
            UnitID.DRONE,       # 30
            UnitID.OVERLORD,    # 30
            UnitID.DRONE,       # 31
            UnitID.DRONE,       # 32
            UnitID.OVERLORD,    # 32
            "BUILD ORDER FINISHED",
        ]
        # current step of the buildorder
        self.buildorder_step = 0
        # expansion we need to clear next, changed in 'send_idle_army'
        self.army_target = None
        # generator we need to cycle through expansions, created in 'send_idle_army'
        self.clear_map = None
        # unit groups, created in 'initialize_unitgroups'
        self.drones = self.larvae = self.queens = self.army = None

    async def on_step(self, iteration):
        # create selections one time for the whole frame
        my_vars.initialize_unit_groups(self)
        my_vars.initialize_units_types(self)

        # things to only do at the start of the game
        if iteration == 0:
            await self.chat_send("(glhf)")
            await drone_attributes.split_workers(self)

        # initialize build order
        await build_order.do_buildorder(self)

        drone_attributes.fill_extractors(self)
        await queen_attributes.do_inject(self)
        await self.distribute_workers()

        # 2 base roach allin
        if self.buildorder[self.buildorder_step] == "BUILD ORDER FINISHED":
            train_units.train_overlords(self)
            train_units.train_queens(self)
            train_units.train_army(self)

            if (self.time / 60 >= 5):
                attack_force.send_units(self)
                attack_force.control_units(self)
                # self.buildorder_step == "ROACH ALLIN FINISHED"

        # full on macro
        if self.buildorder[self.buildorder_step] == "ROACH ALLIN FINISHED":
            train_units.train_overlords(self)
            train_units.train_drones(self)
            train_units.train_queens(self)
            train_units.train_army(self)

        # initialize post-build order phase 2 (macro)

        # do list of actions of the current step
        await self.do_actions(self.actions)
        # empty list to be ready for new actions in the next frame
        self.actions = []
