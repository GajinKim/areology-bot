import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class BuildStep:

    async def stepLarvaUnit(self):
        current_step = self.buildorder[self.buildorder_step]

        self.actions.append(self.larvae.first.train(current_step))
        print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name} ")
        self.buildorder_step += 1


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

    async def stepExtractor(self):
        current_step = self.buildorder[self.buildorder_step]

        if current_step == UnitID.EXTRACTOR:
            # get geysers that dont have extractor on them
            geysers = self.state.vespene_geyser.filter(lambda g: all(g.position != e.position for e in self.units(UnitID.EXTRACTOR)))
            position = geysers.closest_to(self.start_location)

    async def stepHatchery(self):
        current_step = self.buildorder[self.buildorder_step]

        if current_step == UnitID.HATCHERY:
            position = await self.get_next_expansion()
        # closest worker
        worker = self.workers.closest_to(position)
        # construct building at position
        self.actions.append(worker.build(current_step, position))
        print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
        self.buildorder_step += 1
