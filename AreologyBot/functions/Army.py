import itertools
import random

import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import Point2

class Army:
    async def send_army_to_attack(self):
        if self.supply_used < 190:
            return
        if self.supply_used >= 190:
            # Gather available army units
            army = self.army_units
            for unit in army:
                # If we see enemy units
                if self.known_enemy_ground_units:
                    enemy = self.known_enemy_ground_units.closest_to(unit)
                    self.actions.append(unit.attack(enemy))

    async def send_army_to_defend(self):
        if self.supply_used >= 190:
            return
        if self.supply_used < 190:
            enemies = self.known_enemy_units
            # select only idle units, the other units have tasks already
            army_idle = self.army_units.idle and self.queens.idle
            # send all units to defend
            for unit in army_idle:
                for hatch in self.townhalls:
                    if enemies.closer_than(30.0, hatch).exists:
                        closest_enemy = enemies.closest_to(unit)
                        self.actions.append(unit.attack(closest_enemy))
                    else:
                        return
