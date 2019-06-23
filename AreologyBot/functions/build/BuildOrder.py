import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import Point2

import functions
from functions.build.BuildStep import *

class BuildOrder:
    async def startBuild(self):
        # no point in executing function if you have less than 25 minerals
        if self.minerals < 25:
            return

        current_step = self.buildorder[self.buildorder_step]
        # do nothing if we are done already or dont have enough resources for current step of build order
        if current_step == "ALLIN PHASE" or current_step == "MACRO PHASE" or not self.can_afford(current_step):
            return
        # check if current step needs larva
        if current_step in self.from_larva and self.larvae:
            self.actions.append(self.larvae.first.train(current_step))
            print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name} ")
            self.buildorder_step += 1
        elif current_step == UnitID.EXTRACTOR or current_step == UnitID.HATCHERY:
            await BuildStep.stepExtractor(self)
        elif current_step == UnitID.QUEEN:
            await BuildStep.stepQueen(self)
        elif current_step == AbilID.RESEARCH_ZERGLINGMETABOLICBOOST:
            await BuildStep.stepLingSpeed(self)
