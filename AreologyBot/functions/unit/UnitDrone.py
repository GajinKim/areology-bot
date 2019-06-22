import sc2
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class UnitDrone:
    async def sendEarlyGameScout(self):
        scouting_drone = self.drones[0]
        self.actions.append(scouting_drone.attack(self.enemy_start_locations[0]))

    async def retreatEarlyGameScout(self):
        for drone in self.drones:
            damaged_drone = drone.health < 40
            if damaged_drone and self.time / 60 < 2:
                first_mineral_patch = self.state.mineral_field.closest_to(self.units(UnitID.HATCHERY).first.position)
                self.actions.append(drone.gather(first_mineral_patch))

    async def fillExtractors(self):
        for extractor in self.units(UnitID.EXTRACTOR):
            # returns negative value if not enough workers
            if extractor.surplus_harvesters < 0:
                drones_with_no_minerals = self.drones.filter(lambda unit: not unit.is_carrying_minerals)
                if drones_with_no_minerals:
                    # surplus_harvesters is negative when workers are missing
                    for n in range(-extractor.surplus_harvesters):
                        # prevent crash by only taking the minimum
                        drone = drones_with_no_minerals[min(n, drones_with_no_minerals.amount) - 1]
                        self.actions.append(drone.gather(extractor))

    async def splitWorkers(self):
        # split supply_workers
        for drone in self.drones:
            # find closest mineral patch
            closest_mineral_patch = self.state.mineral_field.closest_to(drone)
            self.actions.append(drone.gather(closest_mineral_patch))
        # only do on_step every nth step, 8 is standard
        self._client.game_step = 8
