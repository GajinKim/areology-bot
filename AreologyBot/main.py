import itertools

import sc2
from sc2.ids.ability_id     import AbilityId as AbilID
from sc2.ids.unit_typeid    import UnitTypeId as UnitID

import functions
from functions.Army         import Army
from functions.Unit         import Unit
from functions.Build        import Build
from functions.Train        import Train
from functions.Variables    import Variables

import phases
from phases.GameStart       import GameStart
from phases.BuildOrder      import BuildOrder
from phases.RoachPush       import RoachPush
from phases.MidGame         import MidGame

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
            UnitID.EXTRACTOR,   # 17/22
            UnitID.SPAWNINGPOOL,# 16/22
            UnitID.DRONE,       # 17/22
            UnitID.DRONE,       # 18/22
            "DRONE SCOUT",      # 18/22
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
        self.buildorder_step = 0 # incremented in BuildOrder
        # expansion we need to clear next, changed in 'send_idle_army'
        self.army_target = None
        # generator we need to cycle through expansions, created in 'send_units'
        self.clear_map = None

        """""""""""
        Phase Variables
        """""""""""
        self.scout_sent         = []    # Build Order
        self.roach_push_started = []    # Roach Push

        """""""""""
        Production
        """""""""""
        self.pause_drone_production = []
        self.pause_queen_production = []
        self.pause_army_production  = []

    async def on_step(self, iteration):
        # Update variables on each step
        self.initialize_variables()
        self.current_step = self.buildorder[self.buildorder_step]

        # Things to only do once at the very start of the game
        if iteration == 0:
            await self.on_game_start()
        # Determine what stage we are currently at
        if self.current_step != "ROACH PUSH" and self.current_step != "MID GAME" and self.current_step != "LATE GAME":
            await self.generic_mechanics()
            await self.on_build_order()
        elif self.current_step == "ROACH PUSH":
            await self.generic_mechanics()
            await self.on_roach_push()
        elif self.current_step == "MID GAME":
            await self.generic_mechanics()
            await self.on_mid_game()
        elif self.current_step == "LATE GAME":
            await self.generic_mechanics()
            await self.on_late_game()

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
        # generic macro functions
        await Army.send_army_to_defend(self)
        await Unit.fill_extractors(self)
        await Unit.inject(self)
        await Unit.micro_units(self)
        await self.distribute_workers()
        # todo - fix this stuff (maybe implement a new class for scouting)
        await Unit.retreat_scout(self)

    """""""""""
    Hard Coded Phases
    """""""""""
    async def on_game_start(self):
        await GameStart.worker_split(self)
        await GameStart.overlord_scout(self)
        await GameStart.greeting(self)

    async def on_build_order(self):
        await BuildOrder.start_build(self)

    """""""""""
    Semi-Hard Coded Phase
    """""""""""
    async def on_roach_push(self):
        await RoachPush.power_up(self)
        await RoachPush.start_push(self)
        await RoachPush.end_push(self)

    """""""""""
    Non-Hard Coded Phases
    Priority: Research > Build > Train > Army > Unit
    """""""""""
    async def on_mid_game(self):
        await MidGame.research_upgrades(self)
        await MidGame.build_structures(self)
        await MidGame.train_units(self)
        await MidGame.army_control(self)
        await MidGame.unit_micro(self)

    # Condition: Not set yet. (todo) - i'll probably make the condition once hive finished
    async def on_late_game(self):
        await Build.hatch_tech_buildings(self)
        await Build.lair_tech_buildings(self)
        await Build.hive_tech_buildings(self)
        await Train.train_overlord(self)
        await Train.train_drone(self)
        await Army.send_army_to_attack(self)
        await Army.send_army_to_defend(self)
