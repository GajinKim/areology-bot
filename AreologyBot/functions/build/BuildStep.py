import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class BuildStep:
    async def stepQueen(self):
        current_step = self.buildorder[self.buildorder_step]
        # tech requirement check
        if not self.spawning_pool_finished:
            return
        hatch = self.units(UnitID.HATCHERY).first
        self.actions.append(hatch.train(UnitID.QUEEN))
        print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
        self.buildorder_step += 1

    async def stepLingSpeed(self):
        current_step = self.buildorder[self.buildorder_step]
        # tech requirement check
        if not self.spawning_pool_finished:
            return
        pool = self.units(UnitID.SPAWNINGPOOL).first
        self.actions.append(pool(AbilID.RESEARCH_ZERGLINGMETABOLICBOOST))
        print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
        self.buildorder_step += 1
