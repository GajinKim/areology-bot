import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import Point2

class BuildOrder:
    async def start_build(self):
        # build defense versus early game aggro
        if self.enemy_cheesing:
            await BuildStep.versus_cheese(self)

        # scouting actions
        if self.current_step == "OVERLORD SCOUT":
            await BuildStep.overlord_scout(self)
        elif self.current_step == "DRONE SCOUT":
            await BuildStep.drone_scout(self)
        else:
            # determine if we can even execute the current step
            if self.current_step == "BUILD OVER" or not self.can_afford(self.current_step):
                return

            # steps that consume larva (drone, zergling, overlord)
            elif self.current_step in self.from_larva and self.larvae:
                await BuildStep.step_larva_unit(self)
            # steps that don't consume larva
            elif self.current_step == UnitID.EXTRACTOR:
                await BuildStep.step_extractor(self)
            elif self.current_step == UnitID.HATCHERY:
                await BuildStep.step_hatchery(self)
            elif self.current_step == UnitID.SPAWNINGPOOL:
                await BuildStep.step_spawning_pool(self)
            elif self.current_step == UnitID.ROACHWARREN:
                await BuildStep.step_roach_warren(self)
            elif self.current_step == UnitID.QUEEN:
                await BuildStep.step_queen(self)
            elif self.current_step == AbilID.RESEARCH_ZERGLINGMETABOLICBOOST:
                await BuildStep.step_ling_speed(self)

class BuildStep:
    # Works for now, maybe move anti-cheese algorithm to its own class (or sub-class) later on.
    async def versus_cheese(self):
        # if we manage to build 20 zerglings (10 x 2), we can assume the push has been held
        if self.zerglings.amount >= 10 and self.spine_crawlers.amount >= 2:
            await self.chat_send('Assuming enemy aggression is over')
            self.enemy_cheesing.append(False)
            self.buildorder_step = 33 # step 33 = "BUILD OVER"
        # prioritize building spine crawlers
        elif len(self.spine_crawlers) + self.already_pending(UnitID.SPINECRAWLER) < 2:
            buildings_around = self.units(UnitID.HATCHERY).first.position.towards(self.main_base_ramp.depot_in_middle, 7) # todo: proper location of spine crawler build
            position = await self.find_placement(building=UnitID.SPINECRAWLER, near=buildings_around, placement_step=4)
            # closest worker builds spine crawler
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.SPINECRAWLER, position))
        # pour extra resources into zerglings
        elif self.larvae and self.minerals > 50:
            self.actions.append(self.larvae.first.train(UnitID.ZERGLING))

    async def drone_scout(self):
        scouting_drone = self.drones[0]
        self.actions.append(scouting_drone.move(self.enemy_start_locations[0]))
        # print console log
        print(f"{self.time_formatted} STEP {self.buildorder_step} DRONE SCOUT")
        self.buildorder_step += 1

    async def overlord_scout(self):
        scouting_overlord = self.overlords[0]
        self.actions.append(scouting_overlord.move(self.enemy_start_locations[0]))
        # print console log
        print(f"{self.time_formatted} STEP {self.buildorder_step} OVERLORD SCOUT")
        self.buildorder_step += 1

    async def step_larva_unit(self):
        if self.enemy_cheesing:
            return
        else:
            self.actions.append(self.larvae.first.train(self.current_step))
            # print console log
            print(f"{self.time_formatted} STEP {self.buildorder_step} {self.current_step.name}")
            self.buildorder_step += 1

    async def step_queen(self):
        if self.enemy_cheesing:
            return
        else:
            # tech requirement check
            if not self.spawning_pool_finished:
                return
            for hatch in self.hatcheries.ready.idle:
                self.actions.append(hatch.train(UnitID.QUEEN))
                # print console log
                print(f"{self.time_formatted} STEP {self.buildorder_step} QUEEN")
                self.buildorder_step += 1

    async def step_ling_speed(self):
        if self.enemy_cheesing:
            return
        else:
            # tech requirement check
            if not self.spawning_pool_finished:
                return
            pool = self.units(UnitID.SPAWNINGPOOL).first
            self.actions.append(pool(self.ling_speed))
            # print console log
            print(f"{self.time_formatted} STEP {self.buildorder_step} METABOLIC BOOST")
            self.buildorder_step += 1

    async def step_extractor(self):
        if self.enemy_cheesing:
            return
        else:
            # closest available geyser
            geysers = self.state.vespene_geyser.filter(lambda g: all(g.position != e.position for e in self.units(UnitID.EXTRACTOR)))
            position = geysers.closest_to(self.start_location)
            # closest worker builds extractor
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.EXTRACTOR, position))
            # print console log
            print(f"{self.time_formatted} STEP {self.buildorder_step} EXTRACTOR")
            self.buildorder_step += 1

    async def step_spawning_pool(self):
        if self.enemy_cheesing:
            return
        else:
            # available building positions
            buildings_around = self.units(UnitID.HATCHERY).first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            position = await self.find_placement(building=self.current_step, near=buildings_around, placement_step=4)
            # closest worker builds spawning pool
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.SPAWNINGPOOL, position))
            # print console log
            print(f"{self.time_formatted} STEP {self.buildorder_step} SPAWNING POOL")
            self.buildorder_step += 1

    async def step_roach_warren(self):
        if self.enemy_cheesing:
            return
        else:
            # available building positions
            buildings_around = self.units(UnitID.HATCHERY).first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            position = await self.find_placement(building=self.current_step, near=buildings_around, placement_step=4)
            # closest worker builds roach warren
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.ROACHWARREN, position))
            # print console log
            print(f"{self.time_formatted} STEP {self.buildorder_step} ROACH WARREN")
            self.buildorder_step += 1

    async def step_hatchery(self):
        if self.enemy_cheesing:
            return
        else:
            # closest expansion location
            position = await self.get_next_expansion()
            # closest worker builds hatchery
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.HATCHERY, position))
            # print console log
            print(f"{self.time_formatted} STEP {self.buildorder_step} EXPAND")
            self.buildorder_step += 1
