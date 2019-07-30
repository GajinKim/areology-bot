import itertools

import sc2
from sc2.ids.ability_id     import AbilityId as AbilID
from sc2.ids.unit_typeid    import UnitTypeId as UnitID

import functions
from functions.Army         import Army
from functions.Unit         import Unit
from functions.Build        import Build
from functions.Train        import Train
from functions.Scouting     import Scouting
from functions.Variables    import Variables

import phases
from phases.GameStart       import GameStart
from phases.BuildOrder      import BuildOrder
from phases.RoachPush       import RoachPush
from phases.MacroPhase      import HatchTech
from phases.MacroPhase      import LairTech
from phases.MacroPhase      import HiveTech

class AreologyBot(sc2.BotAI):
    def __init__(self):
        # list of actions we do on_step
        self.actions = []
        # 2 base roach push build order
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
            "DRONE SCOUT",
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
            "BUILD OVER",
            ]
        self.buildorder_step = 0 # incremented in BuildOrder
        # expansion we need to clear next, changed in 'send_idle_army'
        self.army_target = None
        # generator we need to cycle through expansions, created in 'send_units'
        self.clear_map = None

        """""""""""
        Phase Variables
        """""""""""
        self.scouting_drone     = []
        self.scout_sent         = []    # Build Order
        self.roach_push_started = []    # Roach Push

        """""""""""
        Production
        """""""""""
        self.pause_drone_production = []
        self.pause_queen_production = []
        self.pause_army_production  = []

        """""""""""
        Scouting
        """""""""""
        self.drone_scout_retreated      = []
        self.overlord_scout_retreated   = []
        self.enemy_race         = []
        self.enemy_structures   = []
        self.enemy_cheesing     = []

    async def on_step(self, iteration):
        # Update variables on each step
        self.initialize_variables()
        self.current_step = self.buildorder[self.buildorder_step]

        # Things to only do once at the very start of the game
        if iteration == 0:
            await self.on_game_start()
        # Determine what stage we are currently at

        # Build Order
        if not self.hive_finished and not self.lair_finished and self.current_step != "ROACH PUSH" and self.current_step != "BUILD OVER":
            await self.generic_mechanics()
            await self.on_build_order()
        elif self.hive_finished:
            await self.generic_mechanics()
            await self.on_hive_algorithm()
        elif self.lair_finished:
            await self.generic_mechanics()
            await self.on_lair_algorithm()
        elif self.current_step != "ROACH PUSH":
            await self.generic_mechanics()
            await self.on_hatch_algorithm()
        else:
            await self.generic_mechanics()
            await self.on_roach_push()

        # do list of actions of the current step
        await self.do_actions(self.actions)
        # empty list for next frame
        self.actions = []

    """""""""""
    General Setup
    """""""""""
    def initialize_variables(self):
        Variables.unit_variables(self)
        Variables.building_variables(self)
        Variables.upgrade_variables(self)
        Variables.misc_variables(self)

    async def generic_mechanics(self):
        # macro
        await self.distribute_workers()
        await Unit.fill_extractors(self)
        await Unit.inject(self)
        # micro
        await Army.send_army_to_defend(self)
        await Unit.micro_units(self)
        # scouting / information
        await Scouting.retreat_drone_scout(self)
        await Scouting.retreat_overlord_scout(self)
        await Scouting.return_enemy_race(self)
        await Scouting.return_enemy_cheesing(self)

    """""""""""
    Hard Coded Phases
    """""""""""
    async def on_game_start(self):
        await GameStart.worker_split(self)
        await GameStart.greeting(self)

    async def on_build_order(self):
        await BuildOrder.start_build(self)

    """""""""""
    Soft Coded Phases
    """""""""""
    async def on_roach_push(self):
        await RoachPush.power_up(self)
        await RoachPush.start_push(self)
        await RoachPush.end_push(self)

    """""""""""
    Conditional (Macro) Phases
    Priority: Research > Build > Train > Army > Unit
    """""""""""
    async def on_hatch_algorithm(self):
        await HatchTech.research_upgrades(self)
        await HatchTech.build_structures(self)
        await HatchTech.train_units(self)
        await HatchTech.army_control(self)
        await HatchTech.unit_micro(self)

    async def on_lair_algorithm(self):
        await LairTech.research_upgrades(self)
        await LairTech.build_structures(self)
        await LairTech.train_units(self)
        await LairTech.army_control(self)
        await LairTech.unit_micro(self)

    async def on_hive_algorithm(self):
        await HiveTech.research_upgrades(self)
        await HiveTech.build_structures(self)
        await HiveTech.train_units(self)
        await HiveTech.army_control(self)
        await HiveTech.unit_micro(self)
