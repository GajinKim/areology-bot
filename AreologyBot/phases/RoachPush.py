import functions
from functions.Train import *

class RoachPush:
    async def power_up(self):
        await Train.train_overlord(self)
        await Train.rp_train_queen(self)
        await Train.rp_train_army(self)

    async def start_push(self):
        if self.army_supply >= 35:
            # gather all available army units
            army = self.army_units.idle
            for unit in army:
                # issue an attack command towards the enemy's main
                self.actions.append(unit.attack(self.enemy_start_locations[0]))
                # update variable
                self.roach_push_started.append(True)

    async def end_push(self):
        if not self.roach_push_started:
            return
        if self.minutes >= 10 or self.army_supply < 30:
            await self.chat_send("ending roach push!")
            # gather all surviving army units
            army = self.army_units
            for unit in army:
                # retreat home
                self.actions.append(unit.move(self.hatcheries.first.position))
            # ROACH PUSH -> MACRO PHASE
            self.buildorder_step += 1
