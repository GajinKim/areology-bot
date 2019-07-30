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
    async def hatch_tech_buildings(self):
        # Build Hatchery\
        # Primary Check = must have less than 1 : 20 hatch to drone ratio
        if not self.can_afford(UnitID.HATCHERY):
            return
        self.hatch_limit = self.worker_supply / 20
        if not self.already_pending(UnitID.HATCHERY) and len(self.townhalls) < self.hatch_limit:
            self.pause_army_production.append(True)
            await self.expand_now()
            self.pause_army_production.append(False)

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
            self.pause_army_production.append(True)
            self.pause_drone_production.append(True)
            self.pause_queen_production.append(True)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.game_info.map_center, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.SPAWNINGPOOL, position))
            self.pause_army_production.append(False)
            self.pause_drone_production.append(False)
            self.pause_queen_production.append(False)

        # Build Roach Warren
        if len(self.roach_warrens) + self.already_pending(UnitID.ROACHWARREN) == 0:
            self.pause_army_production.append(True)
            self.pause_drone_production.append(True)
            self.pause_queen_production.append(True)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.game_info.map_center, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.ROACHWARREN, position))
            self.pause_army_production.append(False)
            self.pause_drone_production.append(False)
            self.pause_queen_production.append(False)

        # Build Evolution Chamber
        # Primary check = hatch count must be at least 3
        if not self.can_afford(UnitID.EVOLUTIONCHAMBER) or len(self.townhalls) < 3:
            return
        if len(self.evolution_chambers) + self.already_pending(UnitID.EVOLUTIONCHAMBER) < 2:
            self.pause_army_production.append(True)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.game_info.map_center, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.EVOLUTIONCHAMBER, position))
            self.pause_army_production.append(False)

        # Upgrade to Lair
        # Primary check = hatch count must be at least 3
        if not self.can_afford(UnitID.LAIR) or len(self.townhalls) < 3:
            return
        if len(self.lairs) == 0 and self.spawning_pool_finished and self.hatcheries.idle:
            self.pause_army_production.append(True)
            self.pause_queen_production.append(True)
            hatch = self.units(UnitID.HATCHERY).first
            self.actions.append(hatch(AbilID.UPGRADETOLAIR_LAIR))
            self.pause_army_production.append(False)
            self.pause_queen_production.append(False)

    async def lair_tech_buildings(self):
        # Build Hydralisk Den
        if not self.can_afford(UnitID.HYDRALISKDEN):
            return
        if len(self.hydralisk_dens) == 0 and self.lair_finished:
            self.pause_army_production.append(True)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.game_info.map_center, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.HYDRALISKDEN, position))
            self.pause_army_production.append(False)

        # Build Infestation Pit
        # Primary Check = hydralisk den must be finished
        if not self.can_afford(UnitID.INFESTATIONPIT) and self.hydralisk_den_finished:
            return
        if len(self.infestation_pits) == 0 and self.lair_finished:
            self.pause_army_production.append(True)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.INFESTATIONPIT, position))
            self.pause_army_production.append(False)

        # Upgrade to Hive
        # Primary Check = hatch count must be at least 4
        if not self.can_afford(UnitID.HIVE) or len(self.townhalls) < 4:
            return
        if len(self.hives) == 0 and self.infestation_pits and self.units(UnitID.LAIR).idle:
            self.pause_army_production.append(True)
            self.pause_queen_production.append(True)
            lair = self.units(UnitID.LAIR).first
            self.actions.append(lair(AbilID.UPGRADETOHIVE_HIVE))
            self.pause_army_production.append(False)
            self.pause_queen_production.append(False)

    async def hive_tech_buildings(self):
        return
