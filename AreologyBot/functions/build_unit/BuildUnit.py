import sc2
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class BuildUnit:
    async def trainDrones(self):
        # drones cost 50 minerals
        if self.minerals < 50 or not self.enableDroneProduction:
            return
        # train up to 80 drones
        if self.larvae and self.supply_workers < 80:
            # train up to 22 drones per base
            if self.worker_supply < 22 * self.townhalls.ready.amount:
                self.actions.append(self.larvae.first.train(UnitID.DRONE))

    async def trainQueens(self):
        self.queenCount = self.queens.amount + self.already_pending(UnitID.QUEEN)
        # queens cost 150 minerals
        if self.minerals < 150 or not self.enableQueenProduction:
            return
        # max 3 queens during allin phase
        if self.buildorder[self.buildorder_step] == "ALLIN PHASE":
            if self.spawning_pools and self.queenCount < 3:
                hatch = self.units(UnitID.HATCHERY).first
                self.actions.append(hatch.train(UnitID.QUEEN))
            return
        # max 12 queens during macro phase
        if self.buildorder[self.buildorder_step] == "MACRO PHASE":
            if self.spawning_pools and self.queenCount < 12:
                # train up to 1.5 queens per base
                if self.queenCount < 1.5 * self.townhalls.ready.amount:
                    if self.can_afford(UnitID.QUEEN):
                        hatch = self.units(UnitID.HATCHERY).first
                        self.actions.append(hatch.train(UnitID.QUEEN))
                    return

    async def trainArmy(self):
        # cheapest army unit costs 50 minerals
        if self.minerals < 50 or not self.enableArmyProduction:
            return
        # prioritize workers if somehow have fewer than 15
        if self.larvae and self.worker_supply < 15:
            self.actions.append(self.larvae.first.train(UnitID.DRONE))
        if self.larvae and self.roach_warren_finished:
            if self.can_afford(UnitID.ROACH):
                # note that this only builds one unit per step
                self.actions.append(self.larvae.first.train(UnitID.ROACH))
            # only build zergling if you cant build roach soon
            elif self.minerals >= 50 and self.vespene <= 8:
                self.actions.append(self.larvae.first.train(UnitID.ZERGLING))
        if self.larvae and self.hydralisk_den_finished:
            if self.can_afford(UnitID.HYDRALISK):
                self.actions.append(self.larvae.first.train(UnitID.HYDRALISK))
            elif self.can_afford(UnitID.ROACH):
                self.actions.append(self.larvae.first.train(UnitID.ROACH))

    async def trainOverlords(self):
        # build more overlords after buildorder
        # you need larva and enough minerals
        # prevent overlords if you have reached the cap already
        # calculate if you need more supply
        if (
            self.can_afford(UnitID.OVERLORD)
            and self.larvae
            and self.supply_cap != 200
            and self.supply_left + self.already_pending(UnitID.OVERLORD) * 8 < 3 + self.supply_used // 7
        ):
            self.actions.append(self.larvae.first.train(UnitID.OVERLORD))
