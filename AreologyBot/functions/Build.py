import itertools
import random

import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import Point2

class Build:
    async def hatch_tech_buildings(self):
        # Build Hatchery
        if self.minerals < 300:
            return
        self.hatch_limit = self.supply_workers / 20
        if not self.already_pending(UnitID.HATCHERY) and self.hatcheries.amount < self.hatch_limit:
            self.pause_army_production.append(True)
            await self.expand_now()
            self.pause_army_production.append(False)

        # Build Extractor
        if self.minerals < 25:
            return
        for hatch in self.townhalls.ready:
            for target_vespene in self.state.vespene_geyser.closer_than(10.0, hatch):
                worker = self.workers.closest_to(target_vespene)
                self.actions.append(worker.build(UnitID.EXTRACTOR, target_vespene))

        # Build Spawning Pool
        if self.minerals < 200:
            return
        current_step = self.buildorder[self.buildorder_step]
        # need at least 200 minerals to build a spawning pool
        if self.spawning_pools.amount == 0:
            self.pause_army_production.append(True)
            self.pause_drone_production.append(True)
            position = self.hatcheries.ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.SPAWNINGPOOL, position))
            self.pause_army_production.append(False)
            self.pause_drone_production.append(False)

        # Build Roach Warren
        if self.minerals < 150:
            return
        current_step = self.buildorder[self.buildorder_step]
        # in case warren was destroyed some point after the build phase
        if self.roach_warrens.amount == 0:
            self.pause_army_production.append(True)
            self.pause_drone_production.append(True)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.ROACHWARREN, position))
            self.pause_army_production.append(False)
            self.pause_drone_production.append(False)

        # Build Evolution Chamber
        if self.minerals < 150:
            return
        if self.evolution_chambers.amount < 2 and self.hatcheries.amount + self.lairs.amount >= 3:
            self.pause_army_production.append(True)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.game_info.map_center, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.EVOLUTIONCHAMBER, position))
            self.pause_army_production.append(False)

    async def lair_tech_buildings(self):
        # Upgrade to Lair
        if self.minerals < 150 or self.vespene < 100 or self.hatcheries.amount < 3:
            return
        if self.lairs == 0 and self.spawning_pool_finished and self.units(UnitID.HATCHERY).idle:
            self.pause_army_production.append(True)
            self.pause_drone_production.append(True)
            self.pause_queen_production.append(True)
            hatch = self.units(UnitID.HATCHERY).first
            self.actions.append(hatch(AbilID.UPGRADETOLAIR_LAIR))
            self.pause_army_production.append(False)
            self.pause_drone_production.append(False)
            self.pause_queen_production.append(False)

        # Build Hydralisk Den
        if self.minerals < 100 or self.vespene < 100:
            return
        if self.hydralisk_dens.amount == 0 and self.lair_finished:
            self.pause_army_production.append(True)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.game_info.map_center, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.HYDRALISKDEN, position))
            self.pause_army_production.append(False)

        # Build Infestation Pit
        if self.minerals < 100 or self.vespene < 100:
            return
        if self.infestation_pits.amount and self.lair_finished and self.hydralisk_den_finished:
            self.pause_army_production.append(True)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.INFESTATIONPIT, position))
            self.pause_army_production.append(False)

    async def hive_tech_buildings(self):
        #Upgrade to Hive
        if self.minerals < 200 or self.vespene < 150 or self.hatcheries.amount < 4:
            return
        if self.hives == 0 and self.infestation_pits and self.units(UnitID.LAIR).idle:
            self.pause_army_production.append(True)
            self.pause_drone_production.append(True)
            self.pause_queen_production.append(True)
            lair = self.units(UnitID.LAIR).first
            self.actions.append(lair(AbilID.UPGRADETOHIVE_HIVE))
            self.pause_army_production.append(False)
            self.pause_drone_production.append(False)
            self.pause_queen_production.append(False)
