import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class Unit:
    async def micro_units(self):
        # Roach Micro
        for roach in self.roaches:
            if roach.health < 20:
                threats = self.known_enemy_units.closer_than(roach.ground_range + roach.radius, roach.position)
                if threats.exists and roach.position != threats.closest_to(roach).position:
                    distance = await self._client.query_pathing(roach.position, roach.position.towards(threats.closest_to(roach).position, -2))
                    if distance is None:
                        # path is blocked, just keep attacking
                        self.actions.append(roach.attack(threats.closest_to(roach.position)))
                    else:
                        # move back
                        self.actions.append(roach.move(roach.position.towards(threats.closest_to(roach).position, -2)))
