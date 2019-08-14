import sc2
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class Train:
    """
    Drone / Overlord
    Production
    """
    async def train_drone(self):
        self.worker_cap = min(16 * (len(self.hatcheries) + len(self.lairs) + len(self.hives)) + 3 * len(self.extractors), 80)
        if self.minerals < 50 or self.worker_supply > 1.25 * self.army_supply or self.pause_drone_production:
            return
        # Soft Cap is num of hatcheries * 22 + building hatcheries * 6
        # Hard Cap is 80
        if self.larvae and self.worker_supply < self.worker_cap:
            self.actions.append(self.larvae.first.train(UnitID.DRONE))

    async def train_overlord(self):
        if self.minerals < 100:
            return
        if self.larvae and self.supply_cap != 200 and self.supply_left + self.already_pending(UnitID.OVERLORD) * 8 < 3 + self.supply_used // 7:
            self.actions.append(self.larvae.first.train(UnitID.OVERLORD))

    """
    Queen Production
    """
    async def train_queen(self):
        self.queen_count = self.queens.amount + self.already_pending(UnitID.QUEEN)
        self.queen_cap = min(len(self.townhalls) * 1.5, 12);
        if self.minerals < 150 or self.pause_queen_production:
            return
        # Soft Cap is num of hatcheries * 1.5
        # Hard Cap is 12
        if self.spawning_pool_finished and self.queen_count < self.queen_cap:
            for hatch in self.hatcheries.ready.idle:
                self.actions.append(hatch.train(UnitID.QUEEN))
    """
    Army Production
    """
    async def rp_train_army(self):
        if self.minerals < 50:
            return
        # Prioritization: Roach > Zergling
        if self.larvae and self.roach_warren_finished:
            if self.can_afford(UnitID.ROACH):
                self.actions.append(self.larvae.first.train(UnitID.ROACH))
            elif self.minerals >= 50 and self.vespene <= 8:
                self.actions.append(self.larvae.first.train(UnitID.ZERGLING))

    async def hatch_train_army(self):
        if self.minerals < 50 or self.pause_army_production:
            return
        # If we somehow end up with less than 15 drones, priotize workers
        if self.larvae and self.worker_supply < 15:
            self.actions.append(self.larvae.first.train(UnitID.DRONE))
        # Prioritzation: Roaches > Zerglinging
        if self.larvae and self.roach_warren_finished:
            if self.can_afford(UnitID.ROACH):
                self.actions.append(self.larvae.first.train(UnitID.ROACH))
        # Hard Cap of 15 zerglings
        if self.larvae and self.spawning_pool_finished and self.zerglings.amount < 15:
            if self.can_afford(UnitID.ZERGLING):
                self.actions.append(self.larvae.first.train(UnitID.ZERGLING))

    async def lair_train_army(self):
        if self.minerals < 50:
            return
        # If we somehow end up with less than 15 drones, priotize workers
        if self.larvae and self.worker_supply < 15:
            self.actions.append(self.larvae.first.train(UnitID.DRONE))
        # Prioritzation: Hydralisk > Roach
        if self.larvae and self.hydralisk_den_finished and self.roach_warren_finished:
            if self.can_afford(UnitID.HYDRALISK):
                self.actions.append(self.larvae.first.train(UnitID.HYDRALISK))
            elif self.can_afford(UnitID.ROACH):
                self.actions.append(self.larvae.first.train(UnitID.ROACH))
        if self.larvae and self.roach_warren_finished:
            if self.can_afford(UnitID.ROACH):
                self.actions.append(self.larvae.first.train(UnitID.ROACH))
