import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import Point2

class BuildOrder:
    async def startBuild(self):
        # only try to build something if you have 25 minerals, otherwise you dont have enough anyway
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
        # check if current step needs drone
        elif current_step == UnitID.EXTRACTOR or current_step == UnitID.HATCHERY:
            if current_step == UnitID.EXTRACTOR:
                # get geysers that dont have extractor on them
                geysers = self.state.vespene_geyser.filter(lambda g: all(g.position != e.position for e in self.units(UnitID.EXTRACTOR)))
                position = geysers.closest_to(self.start_location)
            if current_step == UnitID.HATCHERY:
                position = await self.get_next_expansion()
            # closest worker
            worker = self.workers.closest_to(position)
            # construct building at position
            self.actions.append(worker.build(current_step, position))
            print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
            self.buildorder_step += 1
        elif current_step == UnitID.QUEEN:
            # tech requirement check
            if not self.spawning_pool_finished:
                return
            hatch = self.units(UnitID.HATCHERY).first
            self.actions.append(hatch.train(UnitID.QUEEN))
            print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
            self.buildorder_step += 1
        elif current_step == AbilID.RESEARCH_ZERGLINGMETABOLICBOOST:
            # tech requirement check
            if not self.spawning_pool_finished:
                return
            pool = self.units(UnitID.SPAWNINGPOOL).first
            self.actions.append(pool(AbilID.RESEARCH_ZERGLINGMETABOLICBOOST))
            print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
            self.buildorder_step += 1
