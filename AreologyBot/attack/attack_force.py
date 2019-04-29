import itertools
import random

import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import Point2

class attack_force:
    def send_units(self):
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
            for unit in self.army:
                self.actions.append(unit.move(self.army_target))
        else:
            # select only idle units, the other units have tasks already
            army_idle = self.army.idle
            # wait with first attack until we have 5 units
            if army_idle.amount < 6:
                return
            # send all units
            for unit in army_idle:
                # attack closest unit
                closest_enemy = ground_enemies.closest_to(unit)
                self.actions.append(unit.attack(closest_enemy))

    def control_units(self):
        # we can only fight ground units and we dont want to fight larvae
        ground_enemies = self.known_enemy_units.filter(lambda unit: not unit.is_flying and unit.type_id != UnitID.LARVA)
        # no need to do anything here if we dont see anything
        if not ground_enemies:
            return
        army = self.units.filter(lambda unit: unit.type_id in {UnitID.ROACH, UnitID.ZERGLING})
        # create selection of dangerous enemy units.
        # bunker and uprooted spine dont have weapon, but should be in that selection
        # also add spinecrawler and cannon if they are not ready yet and have no weapon
        enemy_fighters = ground_enemies.filter(
            lambda u: u.can_attack
            or u.type_id in {UnitID.BUNKER, UnitID.SPINECRAWLERUPROOTED, UnitID.SPINECRAWLER, UnitID.PHOTONCANNON}
        )
        for unit in army:
            if enemy_fighters:
                # select enemies in range
                in_range_enemies = enemy_fighters.in_attack_range_of(unit)
                if in_range_enemies:
                    # prioritize works if in range
                    workers = in_range_enemies({UnitID.DRONE, UnitID.SCV, UnitID.PROBE})
                    if workers:
                        in_range_enemies = workers
                    # special micro for ranged units
                    if unit.ground_range > 1:
                        # attack if weapon not on cooldown
                        if unit.weapon_cooldown == 0:
                            # attack enemy with lowest hp of the ones in range
                            lowest_hp = min(in_range_enemies, key=lambda e: e.health + e.shield)
                            self.actions.append(unit.attack(lowest_hp))
                        else:
                            closest_enemy = enemy_fighters.closest_to(unit)
                            self.actions.append(unit.move(closest_enemy.position.towards(unit, unit.ground_range)))
                    else:
                        # target fire with lings
                        lowest_hp = min(in_range_enemies, key=lambda e: e.health + e.shield)
                        self.actions.append(unit.attack(lowest_hp))
                else:
                    # no unit in range, go to closest
                    self.actions.append(unit.move(enemy_fighters.closest_to(unit)))
            else:
                # no dangerous enemy at all, attack closest of everything
                self.actions.append(unit.attack(ground_enemies.closest_to(unit)))
