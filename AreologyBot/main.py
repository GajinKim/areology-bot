import itertools, random, math

import sc2, build, macro, micro, train
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import Point2

from build.build_order import *

from macro.macro_drones import *
from macro.macro_queens import *
from macro.Essentials import *

from train.train_units import *

from my_vars import *

# from attributes.queen_injects import inject

class AreologyBot(sc2.BotAI):
    def __init__(self):
        # list of actions we do at each step
        self.actions = []
        # set of things that come from a larva
        self.from_larva = {UnitID.DRONE, UnitID.OVERLORD, UnitID.ZERGLING, UnitID.MUTALISK}
        # set of things that come from a drone
        self.from_drone = {UnitID.HATCHERY, UnitID.SPAWNINGPOOL, UnitID.EXTRACTOR, UnitID.BANELINGNEST, UnitID.EVOLUTIONCHAMBER, UnitID.SPIRE}
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
            UnitID.DRONE,       # 21/22
            # should start metabolic boost at 21
            UnitID.DRONE,       # 22
            UnitID.QUEEN,       # 24
            UnitID.QUEEN,       # 26
            "END",
        ]
        # current step of the buildorder
        self.buildorder_step = 0
        # expansion we need to clear next, changed in 'send_idle_army'
        self.army_target = None
        # generator we need to cycle through expansions, created in 'send_idle_army'
        self.clear_map = None
        # unit groups, created in 'set_unit_groups'
        self.drones = None
        self.larvae = None
        self.queens = None
        self.ground_army = None
        self.air_army = None

    async def on_step(self, iteration):
        # create selections one time for the whole frame
        my_vars.initialize_unit_groups(self)
        my_vars.initialize_units_types(self)

        # initialize build order
        if iteration == 0:
            await Essentials.start_step(self)
        await build_order.do_buildorder(self)

        await macro_queens.do_inject(self)
        macro_drones.fill_extractors(self)

        # initialize post-build order phase
        if self.buildorder[self.buildorder_step] == "END":
            train_units.build_army(self)
            train_units.build_overlords(self)

        # do list of actions of the current step
        await self.do_actions(self.actions)
        # empty list to be ready for new actions in the next frame
        self.actions = []
