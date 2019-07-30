import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class Unit:
    """
    Drone Functions
    """
    async def fill_extractors(self):
        for extractor in self.extractors:
            # returns negative value if not enough workers
            if extractor.surplus_harvesters < 0:
                drones_with_no_minerals = self.drones.filter(lambda unit: not unit.is_carrying_minerals)
                if drones_with_no_minerals:
                    # surplus_harvesters is negative when workers are missing
                    for n in range(-extractor.surplus_harvesters):
                        # prevent crash by only taking the minimum
                        drone = drones_with_no_minerals[min(n, drones_with_no_minerals.amount) - 1]
                        self.actions.append(drone.gather(extractor))

    """
    Queen Functions
    """
    async def inject(self):
        if not self.queens:
            return
        for queen in self.queens.idle:
            abilities = await self.get_available_abilities(queen)
            # check if queen can inject
            # you could also use queen.energy >= 25 to save the async call
            if AbilID.EFFECT_INJECTLARVA in abilities:
                hatch = self.units(UnitID.HATCHERY).first
                self.actions.append(queen(AbilID.EFFECT_INJECTLARVA, hatch))

    """
    Army Micro Functions
    """
    async def micro_units(self): # doesn't really work as intended, fix it later
        # Roach Micro
        for roach in self.roaches:
            if roach.health < 30:
                threats = self.known_enemy_units.closer_than(roach.ground_range + roach.radius, roach.position)
                if threats.exists and roach.position != threats.closest_to(roach).position:
                    distance = await self._client.query_pathing(roach.position, roach.position.towards(threats.closest_to(roach).position, -2))
                    if distance is None:
                        # path is blocked, just keep attacking
                        self.actions.append(roach.attack(threats.closest_to(roach.position)))
                    else:
                        # move back
                        self.actions.append(roach.move(roach.position.towards(threats.closest_to(roach).position, -2)))
