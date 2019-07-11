import functions
from functions.Train import *
from functions.Unit import *

class RoachPush:
    async def power_up(self):
        await Train.train_overlord(self)
        await Train.train_queen(self)
        await Train.rp_train_army(self)

    async def start_push(self):
        if self.army_supply >= 35:
            # Update Status
            if not self.roach_push_started:
                self.roach_push_started.append(True)
                await self.chat_send("starting roach push!")
            # Gather available army units
            army = self.army_units
            for unit in army:
                # If we see enemy units
                if self.known_enemy_ground_units:
                    enemy = self.known_enemy_ground_units.closest_to(unit)
                    self.actions.append(unit.attack(enemy))
                # If we don't see any hostile enemies
                else:
                    if not self.clear_map:
                        self.clear_map = itertools.cycle([self.enemy_start_locations[0]] + list(self.expansion_locations.keys()))
                        self.army_target = next(self.clear_map)
                    if self.units.closer_than(7, self.army_target):
                        self.army_target = next(self.clear_map)
                        self.actions.append(unit.move(self.army_target))

    async def end_push(self):
        if not self.roach_push_started:
            return
        if self.army_supply < 30:
            # Update Status
            self.buildorder_step += 1
            await self.chat_send("ending roach push!")

            # Retreat surviving army units
            army = self.army_units
            for unit in army:
                self.actions.append(unit.move(self.hatcheries.first.position))
