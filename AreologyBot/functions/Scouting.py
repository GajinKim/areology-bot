import sc2
from sc2 import Race
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class Scouting:
    """
    Scouting Units
    """
    async def retreat_drone_scout(self):
        if self.drone_scout_retreated:
            return
        else:
            for drone in self.drones:
                if self.time > 2.1:
                    first_mineral_patch = self.state.mineral_field.closest_to(self.hatcheries.first.position)
                    self.actions.append(drone.gather(first_mineral_patch))
                    self.drone_scout_retreated = True
                else:
                    return

    async def retreat_overlord_scout(self):
        if self.overlord_scout_retreated:
            return
        else:
            for overlord in self.overlords:
                damaged_overlord = overlord.health < 200
                if damaged_overlord:
                    # damaged overlord sent back home
                    self.actions.append(overlord.move(self.hatcheries.first.position))
                    self.overlord_scout_retreated = True

    """
    Gathered Information
    """
    async def return_enemy_race(self):
        # do nothing if we already know the enemy's race
        if (self.enemy_race == Race.Terran or self.enemy_race == Race.Zerg or self.enemy_race == Race.Protoss):
            return
        # scenario 1: we cross paths with the enemy's scouting unit
        elif self.known_enemy_units.exists:
            if len(self.known_enemy_units(UnitID.SCV)) > 0:
                self.enemy_race = Race.Terran
            elif len(self.known_enemy_units(UnitID.DRONE)) + len(self.known_enemy_units(UnitID.OVERLORD)) > 0:
                self.enemy_race = Race.Zerg
            elif len(self.known_enemy_units(UnitID.PROBE)) > 0:
                self.enemy_race = Race.Protoss
        # scenario 2: we arrive at the enemy's base
        elif self.known_enemy_structures.exists:
            if self.known_enemy_structures(UnitID.COMMANDCENTER).exists:
                self.enemy_race = Race.Terran
            elif self.known_enemy_structures(UnitID.HATCHERY).exists:
                self.enemy_race = Race.Zerg
            elif self.known_enemy_structures(UnitID.NEXUS).exists:
                self.enemy_race = Race.Protoss

    async def return_enemy_cheesing(self):
        if self.enemy_cheesing or self.current_step == "BUILD OVER":
            return
        if self.enemy_race == Race.Terran:
            # scenario 1: late / no expansion
            if self.minutes > 2 and len(self.known_enemy_structures(UnitID.COMMANDCENTER)) < 2:
                self.enemy_cheesing.append(True)
                await self.chat_send("ENEMY BE PROXYING")
        elif self.enemy_race == Race.Zerg:
            # scenario 1: late / no expansion
            if self.minutes > 2 and len(self.known_enemy_structures(UnitID.HATCHERY)) < 2:
                self.enemy_cheesing.append(True)
                await self.chat_send("ENEMY BE CHEESING")
        elif self.enemy_race == Race.Protoss:
            # scenario 1: late / no expansion
            if self.minutes > 2 and len(self.known_enemy_structures(UnitID.NEXUS)) < 2:
                self.enemy_cheesing.append(True)
                await self.chat_send("ENEMY BE CHEESING")
