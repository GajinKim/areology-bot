import itertools, random, math

import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import *

import functions
from functions.Army import *
from functions.Unit import *
from functions.Build import *
from functions.Train import *
from functions.GlobalVariables import *
from functions.BuildOrder import *


class AreologyBot(sc2.BotAI):
    def __init__(self):
        # list of actions we do at each step
        self.actions = []
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
            "ROACH PUSH",
            "MID GAME",
            "LATE GAME"
            ]
        self.buildorder_step = 0
        self.buildorder_step_name = self.buildorder[self.buildorder_step]
        # expansion we need to clear next, changed in 'send_idle_army'
        self.army_target = None
        # generator we need to cycle through expansions, created in 'send_units'
        self.clear_map = None

        """""""""""
        initialize_global_variables()
        """""""""""
        # Building Variables
        self.hatcheries = self.lairs = self.hives = None
        self.extractors = self.spawning_pools = self.evolution_chambers = self.spine_crawlers = self.spore_crawlers = self.roach_warrens = self.baneling_nests = None
        self.hydralisk_dens = self.lurker_dens = self.infestation_pits = self.spires = self.ultra_caverns = self.greater_spires = None
        self.lair_finished = self.hive_finished = self.spawning_pool_finished = self.roach_warren_finished = self.baneling_nest_finished = False
        self.hydralisk_den_finished = self.lurker_den_finished = self.infestation_pit_finished = self.spire_finished = self.ultra_cavern_finished = self.greater_spire_finished = False
        # Unit Variables
        self.larvae = self.drones = self.queens = self.zerglings = self.banelings = self.roaches = self.ravagers = self.hydralisks = self.lurkers = self.infestors = self.infested_terrans = None
        self.swarm_hosts = self.locusts = self.ultralisks = self.overlords = self.overseers = self.changelings = self.mutalisks = self.corruptors = self.vipers = self.brood_lords = self.broodlings = None
        # Misc. Variables
        self.from_larva = self.from_drone = None
        self.armyUnits = self.droneSupply = self.armySupply = None

        """""""""""
        Production
        """""""""""
        self.pause_drone_production = []
        self.pause_queen_production = []
        self.pause_army_production  = []

    async def on_step(self, iteration):
        # Generic Setup
        self.initialize_global_variables()

        # Things to only do once at the very start of the game
        if iteration == 0:
            await self.on_game_start()
        # Determine what stage we are currently at
        if self.buildorder_step_name != ("ROACH PUSH" or "MID GAME" or "LATE GAME"):
            await self.on_build_order()
        elif self.buildorder_step_name == "ROACH PUSH":
            await self.on_roach_push()
        elif self.buildorder_step_name == "MID GAME":
            await self.on_mid_game()
        elif self.buildorder_step_name == "LATE GAME":
            await self.on_late_game()

        # await self.generic_mechanics()

        # do list of actions of the current step
        await self.do_actions(self.actions)
        # empty list to be ready for new actions in the next frame
        self.actions = []

    """""""""""
    General Setup
    """""""""""
    def initialize_global_variables(self):
        GlobalVariables.unit_variables(self)
        GlobalVariables.building_variables(self)
        GlobalVariables.upgrade_variables(self)
        GlobalVariables.misc_variables(self)

    async def generic_mechanics(self):
        # generic macro functions
        await Unit.fill_extractors(self)
        await Unit.inject(self)
        await Unit.micro_units(self)
        await self.distribute_workers()

    """
    Hard Coded Actions
    """
    async def on_game_start(self):
        await Unit.drone_split(self)
        await Unit.drone_scout(self)
        await Unit.overlord_scout(self)
        await self.chat_send("(glhf)")

    async def on_build_order(self):
        await BuildOrder.execute_build(self)
        await Unit.drone_scout_retreat(self)
        await Unit.overlord_scout_retreat(self)

    """""""""""
    Semi-Hard Coded Actions
    """""""""""
    # Condition: Build order is finished
    async def on_roach_push(self):
        await Train.train_overlord(self)
        await Train.rp_train_queen(self)
        await Train.rp_train_army(self)
        await Army.two_base_push(self)

    """""""""""
    Non-Hard Coded Actions
    Priority: Upgrade > Build > Train > Army / Unit
    """""""""""
    # Condition: 2 Base Roach Push is over
    async def on_mid_game(self):
        await Build.hatch_tech_buildings(self)
        await Build.lair_tech_buildings(self)
        await Train.train_overlord(self)
        await Train.train_drone(self)
        await Train.mg_train_queen(self)
        await Train.mg_train_army(self)
        await Army.sendUnitsToDefend(self)
        await Army.sendUnitsToAttack(self)
        await Unit.micro_units(self)

    # Condition: Not set yet. (todo)
    async def on_late_game(self):
        await Build.hatch_tech_buildings(self)
        await Build.lair_tech_buildings(self)
        await Build.hive_tech_buildings(self)
        await Train.train_overlord(self)
        await Train.train_drone(self)
