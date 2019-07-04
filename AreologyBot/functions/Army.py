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
            # we can only fight ground units and we dont want to fight larvae
            ground_enemies = self.known_enemy_units.filter(lambda unit: not unit.is_flying and unit.type_id != UnitID.LARVA)
            # we dont see anything, go to enemy start location (only works on 2 player maps)
            if not ground_enemies:
                # if we didnt start to clear the map already
                if not self.clear_map:
                    # start with enemy starting location, then cycle through all expansions
                    self.clear_map = itertools.cycle(
                        [self.enemy_start_locations[0]] + list(self.expansion_locations.keys())
                    )
                    self.army_target = next(self.clear_map)
                # we can see the expansion but there seems to be nothing, get next
                if self.units.closer_than(7, self.army_target):
                    self.army_target = next(self.clear_map)
                # send all units
                for unit in self.army_units:
                    self.actions.append(unit.move(self.army_target))
            else:
                # select only idle units, the other units have tasks already
                army_idle = self.army_units.idle
                # send all units
                for unit in army_idle:
                    # attack closest unit
                    closest_enemy = ground_enemies.closest_to(unit)
                    self.actions.append(unit.attack(closest_enemy))

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
