import sc2
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class Train:

    """
    Drone / Overlord
    Production
    """
    async def train_drone(self):
        # drones cost 50 minerals
        if self.minerals < 50 or not self.enable_drone_production:
            return
        # train up to 80 drones
        if self.larvae and self.supply_workers < 80:
            # train up to 22 drones per base
            if self.worker_supply < 22 * self.townhalls.ready.amount:
                self.actions.append(self.larvae.first.train(self.drones))

    async def train_overlord(self):
        if (
            self.can_afford(UnitID.OVERLORD)
            and self.larvae
            and self.supply_cap != 200
            and self.supply_left + self.already_pending(self.overlords) * 8 < 3 + self.supply_used // 7
        ):
            self.actions.append(self.larvae.first.train(self.overlords))

    """
    Queen Production
    """
    async def rp_train_queen(self):
        if self.minerals < 150 or not self.enable_queen_production:
            return
        # max 3 queen roach push phase
        if self.spawning_pool_finished and self.units(self.queens).amount + self.already_pending(self.units(self.queens)) < 3:
            if self.can_afford(self.queens):
                hatch = self.units(self.hatcheries).first
                self.actions.append(hatch.train(self.queens))

    async def mg_train_queen(self):
        if self.minerals < 150 or not self.enable_queen_production:
            return
        # 12 Queen Cap
        if self.spawning_pool_finished and self.units(self.queens).amount + self.already_pending(self.units(self.queens)) < 12:
            # 1.5 Queens per Base
            if self.queenCount < 1.5 * self.townhalls.ready.amount:
                if self.can_afford(self.queens):
                    hatch = self.units(self.hatcheries).first
                    self.actions.append(hatch.train(self.queens))
    """
    Army Production
    """
    async def rp_train_army(self):
        if self.minerals < 50 or not self.enable_army_production:
            return
        # Prioritization: Roach > Zergling
        if self.larvae and self.roach_warren_finished:
            if self.can_afford(self.roaches):
                self.actions.append(self.larvae.first.train(self.roaches))
            elif self.minerals >= 50 and self.vespene <= 8:
                self.actions.append(self.larvae.first.train(self.zerglings))

    async def mg_train_army(self):
        if self.minerals < 50 or not self.enable_army_production:
            return
        # If we somehow end up with less than 15 drones, build them first
        if self.larvae and self.worker_supply < 15:
            self.actions.append(self.larvae.first.train(self.drones))
        # Prioritzation: Hydralisk > Roach
        elif self.larvae and self.hydralisk_den_finished and self.roach_warren_finished:
            if self.can_afford(self.hydras):
                self.actions.append(self.larvae.first.train(self.hydras))
            elif self.can_afford(self.roaches):
                self.actions.append(self.larvae.first.train(self.roaches))
        elif self.larvae and self.roach_warren_finished:
            if self.can_afford(self.roaches):
                self.actions.append(self.larvae.first.train(self.roaches))
