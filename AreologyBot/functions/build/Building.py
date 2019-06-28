import itertools
import random

import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import Point2

class Building:
    async def buildSpawningPool(self):
        if self.minerals < 200:
            return
        # build order spawning pool
        current_step = self.buildorder[self.buildorder_step]
        if current_step == UnitID.SPAWNINGPOOL:
            buildings_around = self.units(UnitID.HATCHERY).first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            position = await self.find_placement(building=current_step, near=buildings_around, placement_step=4)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(current_step, position))
            print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
            self.buildorder_step += 1
        # in case pool was destroyed some point after the build phase
        elif self.spawning_pools == 0 and (current_step == "ALLIN PHASE" or current_step == "MACRO PHASE"):
            self.pauseArmyProduction.append(False)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.SPAWNINGPOOL, position))
            self.pauseArmyProduction.append(True)

    async def buildRoachWarren(self):
        if self.minerals < 150:
            return
        # build order roach warren
        current_step = self.buildorder[self.buildorder_step]
        if current_step == UnitID.ROACHWARREN:
            buildings_around = self.units(UnitID.HATCHERY).first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            position = await self.find_placement(building=current_step, near=buildings_around, placement_step=4)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(current_step, position))
            print(f"{self.time_formatted} STEP {self.buildorder_step} {current_step.name}")
            self.buildorder_step += 1
        # in case roach warren was destroyed some point after the build phase
        elif self.roach_warrens == 0 and (current_step == "ALLIN PHASE" or current_step == "MACRO PHASE"):
            self.pauseArmyProduction.append(False)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.ROACHWARREN, position))
            self.pauseArmyProduction.append(True)

    async def upgradeToLair(self):
        if self.minerals < 150 or self.vespene < 100 or self.hatcheries < 3:
            return
        if self.lairs == 0 and self.spawning_pool_finished and self.units(UnitID.HATCHERY).idle:
            self.pauseQueenProduction.append(False)
            self.pauseArmyProduction.append(False)
            hatch = self.units(UnitID.HATCHERY).first
            self.actions.append(hatch(AbilID.UPGRADETOLAIR_LAIR))
            self.pauseQueenProduction.append(False)
            self.pauseArmyProduction.append(False)

    async def upgradeToHive(self):
        if self.minerals < 200 or self.vespene < 150 or self.hatcheries < 4:
            return
        if self.hives == 0 and self.infestation_pits and self.units(UnitID.LAIR).idle:
            self.pauseQueenProduction.append(False)
            self.pauseArmyProduction.append(False)
            lair = self.units(UnitID.LAIR).first
            self.actions.append(lair(AbilID.UPGRADETOHIVE_HIVE))
            self.pauseQueenProduction.append(True)
            self.pauseArmyProduction.append(True)

    async def buildHatcheries(self):
        self.hatch_limit = self.supply_workers / 20
        if self.minerals < 300:
            return
        if not self.already_pending(UnitID.HATCHERY) and self.hatcheries < self.hatch_limit:
            self.pauseArmyProduction.append(False)
            await self.expand_now()
            self.pauseArmyProduction.append(True)

    async def buildExtractors(self):
        if self.minerals < 25:
            return
        for hatch in self.townhalls.ready:
            for target_vespene in self.state.vespene_geyser.closer_than(10.0, hatch):
                worker = self.select_build_worker(target_vespene)
                self.actions.append(worker.build(UnitID.EXTRACTOR, target_vespene))

    async def buildEvolutionChambers(self):
        if self.minerals < 75:
            return
        if self.evolution_chambers < 2 and self.hatcheries + self.lairs >= 3:
            self.pauseArmyProduction.append(False)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.game_info.map_center, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.EVOLUTIONCHAMBER, position))
            self.pauseArmyProduction.append(True)

    async def buildHydraliskDen(self):
        if self.minerals < 100 or self.vespene < 100:
            return
        if self.hydralisk_dens == 0 and self.lair_finished:
            self.pauseArmyProduction.append(False)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.game_info.map_center, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.HYDRALISKDEN, position))
            self.pauseArmyProduction.append(True)

    async def buildInfestationPit(self):
        if self.minerals < 100 or self.vespene < 100:
            return
        if self.infestation_pits == 0 and self.lair_finished and self.hydralisk_den_finished:
            self.pauseArmyProduction.append(False)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.INFESTATIONPIT, position))
            self.pauseArmyProduction.append(True)
