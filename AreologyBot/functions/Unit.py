import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class Unit:
    """
    Drone Functions
    """
    # split workers as soon as the game starts
    async def worker_split(self):
        for drone in self.drones:
            # find closest mineral patch
            closest_mineral_patch = self.state.mineral_field.closest_to(drone)
            self.actions.append(drone.gather(closest_mineral_patch))
        # only do on_step every nth step, 8 is standard
        self._client.game_step = 8

    async def send_drone_scout(self):
        scouting_drone = self.drones[0]
        self.actions.append(scouting_drone.attack(self.enemy_start_locations[0]))

    async def retreat_drone_scout(self):
        for drone in self.drones:
            damaged_drone = drone.health < 40
            if damaged_drone and self.time / 60 < 2:
                first_mineral_patch = self.state.mineral_field.closest_to(self.units(UnitID.HATCHERY).first.position)
                self.actions.append(drone.gather(first_mineral_patch))

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
    Overlord Functions
    """
    async def send_overlord_scout(self):
        scouting_overlord = self.overlords[0]
        self.actions.append(scouting_overlord.move(self.enemy_start_locations[0]))

    async def retreat_overlord_scout(self):
        for overlord in self.units(UnitID.OVERLORD):
            damaged_overlord = overlord.health < 200
            if damaged_overlord:
                # damaged overlord sent back home
                self.actions.append(overlord.move(self.units(UnitID.HATCHERY).first.position))

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
    async def micro_units(self):
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
