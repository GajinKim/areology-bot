import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import Point2

class BuildOrder:
    async def start_build(self):
        # Determine if we can even execute the current step
        if self.current_step == "SEND DRONE SCOUT":
            await BuildStep.drone_scout(self)
        elif not self.can_afford(self.current_step):
            return
            
        # steps that consume larva (drone, zergling, overlord)
        if self.current_step in self.from_larva and self.larvae:
            await BuildStep.step_larva_unit(self)
        # steps that don't consume larva
        if self.current_step == UnitID.EXTRACTOR:
            await BuildStep.step_extractor(self)
        if self.current_step == UnitID.HATCHERY:
            await BuildStep.step_hatchery(self)
        if self.current_step == UnitID.SPAWNINGPOOL:
            await BuildStep.step_spawning_pool(self)
        if self.current_step == UnitID.ROACHWARREN:
            await BuildStep.step_roach_warren(self)
        if self.current_step == UnitID.QUEEN:
            await BuildStep.step_queen(self)
        if self.current_step == AbilID.RESEARCH_ZERGLINGMETABOLICBOOST:
            await BuildStep.step_ling_speed(self)

class BuildStep:
    async def drone_scout(self):
        scouting_drone = self.drones[0]
        self.actions.append(scouting_drone.attack(self.enemy_start_locations[0]))
        # print console log
        print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
        self.buildorder_step += 1

    async def step_larva_unit(self):
        current_step = self.buildorder[self.buildorder_step]
        self.actions.append(self.larvae.first.train(current_step))
        # print console log
        print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
        self.buildorder_step += 1

    async def step_queen(self):
        current_step = self.buildorder[self.buildorder_step]
        # tech requirement check
        if not self.spawning_pool_finished:
            return
        for hatch in self.hatcheries.ready.idle:
            self.actions.append(hatch.train(UnitID.QUEEN))
            # print console log
            print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
            self.buildorder_step += 1

    async def step_ling_speed(self):
        current_step = self.buildorder[self.buildorder_step]
        # tech requirement check
        if not self.spawning_pool_finished:
            return
        pool = self.units(UnitID.SPAWNINGPOOL).first
        self.actions.append(pool(self.ling_speed))
        # print console log
        print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
        self.buildorder_step += 1

    async def step_extractor(self):
        current_step = self.buildorder[self.buildorder_step]
        # closest available geyser
        geysers = self.state.vespene_geyser.filter(lambda g: all(g.position != e.position for e in self.units(UnitID.EXTRACTOR)))
        position = geysers.closest_to(self.start_location)
        # closest worker builds extractor
        worker = self.workers.closest_to(position)
        self.actions.append(worker.build(current_step, position))
        # print console log
        print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
        self.buildorder_step += 1

    async def step_spawning_pool(self):
        current_step = self.buildorder[self.buildorder_step]
        # available building positions
        buildings_around = self.units(UnitID.HATCHERY).first.position.towards(self.main_base_ramp.depot_in_middle, 7)
        position = await self.find_placement(building=current_step, near=buildings_around, placement_step=4)
        # closest worker builds spawning pool
        worker = self.workers.closest_to(position)
        self.actions.append(worker.build(current_step, position))
        # print console log
        print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
        self.buildorder_step += 1

    async def step_roach_warren(self):
        current_step = self.buildorder[self.buildorder_step]
        # available building positions
        buildings_around = self.units(UnitID.HATCHERY).first.position.towards(self.main_base_ramp.depot_in_middle, 7)
        position = await self.find_placement(building=current_step, near=buildings_around, placement_step=4)
        # closest worker builds roach warren
        worker = self.workers.closest_to(position)
        self.actions.append(worker.build(current_step, position))
        # print console log
        print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
        self.buildorder_step += 1

    async def step_hatchery(self):
        current_step = self.buildorder[self.buildorder_step]
        # closest expansion location
        position = await self.get_next_expansion()
        # closest worker builds hatchery
        worker = self.workers.closest_to(position)
        self.actions.append(worker.build(current_step, position))
        # print console log
        print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
        self.buildorder_step += 1
