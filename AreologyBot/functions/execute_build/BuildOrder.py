import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import Point2

import functions
from functions.execute_build.BuildStep import *

class BuildOrder:
    async def execute_build(self):
        # nothing costs less than 25 minerals (except deez nutz)
        if self.minerals < 25:
            return
        # get current step
        current_step = self.buildorder[self.buildorder_step]
        # check that we're in the correct phase and we have enough resources
        if current_step == "ALLIN PHASE" or current_step == "MACRO PHASE" or not self.can_afford(current_step):
            return

        # steps that consume larva (drone, zergling, overlord)
        if current_step in self.from_larva and self.larvae:
            await BuildStep.step_larva_unit(self)

        # steps that don't consume larva
        if current_step == UnitID.EXTRACTOR:
            await BuildStep.step_extractor(self)
        if current_step == UnitID.HATCHERY:
            await BuildStep.step_hatchery(self)
        if current_step == UnitID.SPAWNINGPOOL:
            await BuildStep.step_spawning_pool(self)
        if current_step == UnitID.ROACHWARREN:
            await BuildStep.step_roach_warren(self)
        if current_step == UnitID.QUEEN:
            await BuildStep.step_queen(self)
        if current_step == AbilID.RESEARCH_ZERGLINGMETABOLICBOOST:
            await BuildStep.step_ling_speed(self)
