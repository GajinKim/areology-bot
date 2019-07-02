import sc2
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class Train:
    """
    Drone / Overlord
    Production
    """
    async def train_drone(self):
        # drones cost 50 minerals
        if self.minerals < 50 or self.pause_drone_production or self.worker_supply * 1.25 > self.army_supply:
            return
        # train up to 80 drones
        if self.larvae and self.supply_workers < 80:
            # train up to 22 drones per base
            if self.worker_supply < 22 * self.townhalls.amount:
                self.actions.append(self.larvae.first.train(UnitID.DRONE))

    async def train_overlord(self):
        if self.minerals < 100:
            return
        if self.larvae and self.supply_cap != 200 and self.supply_left + self.already_pending(UnitID.OVERLORD) * 8 < 3 + self.supply_used // 7:
            self.actions.append(self.larvae.first.train(UnitID.OVERLORD))

    """
    Queen Production
    """
    async def rp_train_queen(self):
        self.queen_count = self.queens.amount + self.already_pending(UnitID.QUEEN)
        if self.minerals < 150 or self.pause_queen_production:
            return
        # Roach Push Queen Cap: 3
        if self.spawning_pool_finished and self.queen_count < 3:
            hatch = self.hatcheries.first
            self.actions.append(hatch.train(UnitID.QUEEN))

    async def mg_train_queen(self):
        self.queen_count = self.queens.amount + self.already_pending(UnitID.QUEEN)
        if self.minerals < 150 or self.pause_queen_production:
            return
        # Mid Game Queen Cap: 6
        if self.spawning_pool_finished and self.queen_count < 6:
            # 1.5 Queens per Base
            if self.queen_count < 1.5 * self.townhalls.ready.amount:
                hatch = self.hatcheries.first
                self.actions.append(hatch.train(UnitID.QUEEN))

    async def lg_train_queen(self):
        self.queen_count = self.queens.amount + self.already_pending(UnitID.QUEEN)
        if self.minerals < 150 or self.pause_queen_production:
            return
        # Late Game Queen Cap: 12
        if self.spawning_pool_finished and self.queen_count < 12:
            # 2 Queens per Base
            if self.queen_count < 2 * self.townhalls.ready.amount:
                hatch = self.hatcheries.first
                self.actions.append(hatch.train(UnitID.QUEEN))
    """
    Army Production
    """
    async def rp_train_army(self):
        if self.minerals < 50 or self.pause_army_production:
            return
        # Prioritization: Roach > Zergling
        if self.larvae and self.roach_warren_finished:
            if self.can_afford(UnitID.ROACH):
                self.actions.append(self.larvae.first.train(UnitID.ROACH))
            elif self.minerals >= 50 and self.vespene <= 8:
                self.actions.append(self.larvae.first.train(UnitID.ZERGLING))

    async def mg_train_army(self):
        if self.minerals < 50 or self.pause_army_production:
            return
        # If we somehow end up with less than 15 drones, build them first
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
