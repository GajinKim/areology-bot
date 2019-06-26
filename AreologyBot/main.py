import itertools, random, math

import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import *

import functions
from functions.build_building.BuildBuilding import BuildBuilding as BuildingMake
from functions.build_unit.BuildUnit import BuildUnit as UnitMake

from functions.execute_build.BuildOrder import BuildOrder

from functions.my_army.MyArmy import *
from functions.my_unit.MyDrone import *
from functions.my_unit.MyOverlord import *
from functions.my_unit.MyQueen import *

from GlobalVariables import *

"""
TODO LIST:
- Better optimize drone and overlord scouting patterns
    - currently taking advantage of methods that can cause issues later on and should therefore be removed
- Add early game defense measures from information gathered from scouting
- Refactor this class
- Implement Queen creep spread (possibly use legacy code)
- Fix the attack method, scouting allowed me to realize that there are issues
"""
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
            "ALLIN PHASE",
            "MACRO PHASE"
            ]
        # current step of the buildorder
        self.buildorder_step = 0
        # expansion we need to clear next, changed in 'send_idle_army'
        self.army_target = None
        # generator we need to cycle through expansions, created in 'send_units'
        self.clear_map = None

        """""""""""
        initializeGlobalVariables()
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
        production
        """""""""""
        self.pauseDroneProduction   = []
        self.pauseQueenProduction   = []
        self.pauseArmyProduction    = []

    async def on_step(self, iteration):
        # reinitialize production enablers every step
        self.enableDroneProduction  = [True]
        self.enableQueenProduction  = [True]
        self.enableArmyProduction   = [True]

        # initialize global variables
        self.initializeGlobalVariables()

        # basic mechanics (macro and micro)
        await self.genericMechanics()

        # things to only do at the start of the game
        if iteration == 0:
            await MyDrone.splitWorkers(self)
            await MyDrone.sendScout(self)
            await MyOverlord.sendScout(self)
            await self.chat_send("(glhf)")

        # if we're not not in our allin phase or macro phase we must be in our build order phase
        if not self.buildorder[self.buildorder_step] == "ALLIN PHASE" and not self.buildorder[self.buildorder_step] == "MACRO PHASE": await self.buildOrderPhase()
        if self.buildorder[self.buildorder_step] == "ALLIN PHASE": await self.allinPhase()
        if self.buildorder[self.buildorder_step] == "MACRO PHASE": await self.macroPhase()

        # do list of actions of the current step
        await self.do_actions(self.actions)
        # empty list to be ready for new actions in the next frame
        self.actions = []

    """
    Helper Methods
    """
    def initializeGlobalVariables(self):
        GlobalVariables.buildingVariables(self)
        GlobalVariables.unitVariables(self)
        GlobalVariables.miscVariables(self)

    async def genericMechanics(self):
        # generic macro functions
        await MyDrone.fillExtractors(self)
        await MyQueen.doQueenInjects(self)
        await self.distribute_workers()
        # generic micro functions

    async def buildOrderPhase(self):
        # execute build
        await BuildOrder.executeBuild(self)

        # build order phase micro functions
        await MyDrone.retreatScout(self)
        await MyOverlord.retreatScout(self)

    async def allinPhase(self):
        await UnitMake.trainOverlords(self)
        await UnitMake.trainQueens(self)
        await UnitMake.trainArmy(self)
        # start sending units to attack at 4:00
        await MyArmy.twoBaseAttack(self)

    async def macroPhase(self):
        await BuildingMake.buildHatcheries(self)
        await BuildingMake.upgradeToLair(self)
        await BuildingMake.upgradeToHive(self)
        await BuildingMake.buildExtractors(self)
        await BuildingMake.buildEvolutionChambers(self)
        await BuildingMake.buildSpawningPool(self)
        await BuildingMake.buildRoachWarren(self)
        await BuildingMake.buildHydraliskDen(self)
        await BuildingMake.buildInfestationPit(self)

        await UnitMake.trainOverlords(self)
        await UnitMake.trainDrones(self)
        await UnitMake.trainQueens(self)
        await UnitMake.trainArmy(self)

        await MyArmy.sendUnitsToDefend(self)
        await MyArmy.sendUnitsToAttack(self)
        await MyArmy.microUnits(self)
