import itertools
import random

import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import Point2

"""
LEGEND
Primary Check = Non tech requirements that mandate the production of a building
"""
class Build:
    """
    Hatch Tech Buildings
    """
    async def hatch_tech_buildings(self):
        # Build Hatchery
        # Primary Check = minutes elapsed is cap
        if not self.can_afford(UnitID.HATCHERY):
            return
        self.hatch_limit = min(self.worker_supply / 20 + 1, 4)
        if not self.already_pending(UnitID.HATCHERY) and len(self.townhalls) < self.hatch_limit:
            await self.expand_now()

        # Build Extractor
        if not self.can_afford(UnitID.EXTRACTOR):
            return
        if len(self.extractors) / 2 + 2 <= len(self.townhalls) or self.lairs.exists:
            for hatch in self.hatcheries.ready:
                for target_vespene in self.state.vespene_geyser.closer_than(10.0, hatch):
                    worker = self.workers.closest_to(target_vespene)
                    self.actions.append(worker.build(UnitID.EXTRACTOR, target_vespene))

        # Build Spawning Pool
        if len(self.spawning_pools) + self.already_pending(UnitID.SPAWNINGPOOL) == 0:
            self.pause_drone_production = True
            self.pause_army_production = True
            self.pause_queen_production = True
            buildings_around = self.townhalls.ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            position = await self.find_placement(building=UnitID.SPAWNINGPOOL, near=buildings_around, placement_step=4)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.SPAWNINGPOOL, position))

        # Build Roach Warren
        # Tech Requirements
        if not self.spawning_pool_finished:
            return
        # Extra Requirements: at least 28 workers
        if len(self.roach_warrens) + self.already_pending(UnitID.ROACHWARREN) == 0 and self.worker_supply > 28:
            await self.chat_send('check number of drones, we should be at 28')
            self.pause_drone_production = True
            self.pause_army_production = True
            self.pause_queen_production = True
            buildings_around = self.townhalls.ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            position = await self.find_placement(building=UnitID.ROACHWARREN, near=buildings_around, placement_step=4)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.ROACHWARREN, position))

        # Build Evolution Chamber
        # Extra Requirements: at least 3 bases
        if not self.can_afford(UnitID.EVOLUTIONCHAMBER) or len(self.townhalls) < 3:
            return
        if len(self.evolution_chambers) + self.already_pending(UnitID.EVOLUTIONCHAMBER) < 2:
            self.pause_army_production = True
            buildings_around = self.townhalls.ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            position = await self.find_placement(building=UnitID.EVOLUTIONCHAMBER, near=buildings_around, placement_step=4)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.EVOLUTIONCHAMBER, position))

        # Upgrade to Lair
        # Primary check = hatch count must be at least 3
        # if not self.can_afford(UnitID.LAIR) or len(self.townhalls) < 3 or not self.hatcheries.idle:
        #     return
        # if len(self.lairs) + self.already_pending(UnitID.LAIR) == 0 and self.spawning_pool_finished:
        #     self.pause_army_production.append(True)
        #     self.pause_queen_production.append(True)
        #     hatch = self.units(UnitID.HATCHERY).first
        #     self.actions.append(hatch(AbilID.UPGRADETOLAIR_LAIR))
        #     self.pause_army_production.append(False)
        #     self.pause_queen_production.append(False)

        self.pause_drone_production = False
        self.pause_army_production = False
        self.pause_queen_production = False
    """
    Lair Tech Buildings
    """
    async def lair_tech_buildings(self):
        # Build Hydralisk Den
        if not self.can_afford(UnitID.HYDRALISKDEN):
            return
        if len(self.hydralisk_dens) == 0 and self.lair_finished:
            self.pause_army_production.append(True)
            buildings_around = self.townhalls.ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            position = await self.find_placement(building=UnitID.HYDRALISKDEN, near=buildings_around, placement_step=4)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.HYDRALISKDEN, position))
            self.pause_army_production.append(False)

        # Build Infestation Pit
        # Primary Check = hydralisk den must be finished
        if not self.can_afford(UnitID.INFESTATIONPIT) and self.hydralisk_den_finished:
            return
        if len(self.infestation_pits) == 0 and self.lair_finished:
            self.pause_army_production.append(True)
            buildings_around = self.townhalls.ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            position = await self.find_placement(building=UnitID.INFESTATIONPIT, near=buildings_around, placement_step=4)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.INFESTATIONPIT, position))
            self.pause_army_production.append(False)

        # Upgrade to Hive
        # Primary Check = hatch count must be at least 4
        # if not self.can_afford(UnitID.HIVE) or len(self.townhalls) < 4 or not self.lairs.idle:
        #     return
        # if len(self.hives) + self.already_pending(UnitID.HIVE) == 0 and self.infestation_pits:
        #     self.pause_queen_production.append(True)
        #     lair = self.units(UnitID.LAIR).first
        #     self.actions.append(lair(AbilID.UPGRADETOHIVE_HIVE))
        #     self.pause_queen_production.append(False)

    """
    Hive Tech Buildings
    """
    async def hive_tech_buildings(self):
        return
