import sc2
from sc2.ids.unit_typeid import UnitTypeId as UnitID

# balance drones, queens, overlords, and army
class train_units:
    def train_drones(self):
        # drones cost 50 minerals
        if self.minerals < 50:
            return
        # train up to 80 drones
        if self.larvae and self.supply_workers < 80:
            # train up to 22 drones per base
            if self.supply_workers < 22 * self.townhalls.ready.amount:
                self.actions.append(self.larvae.first.train(UnitID.DRONE))

    def train_queens(self):
        self.supply_queens = self.units(UnitID.QUEEN).amount + self.already_pending(UnitID.QUEEN)
        # queens cost 150 minerals
        if self.minerals < 150:
            return
        # build up to 12 queens
        if self.units(UnitID.SPAWNINGPOOL) and self.supply_queens < 12 and self.units(UnitID.HATCHERY).idle:
            # train up to 1.5 queens per base
            if self.supply_queens < 1.5 * self.townhalls.ready.amount:
                if self.can_afford(UnitID.QUEEN):
                    hatch = self.units(UnitID.HATCHERY).first
                    self.actions.append(hatch.train(UnitID.QUEEN))
                return

    def train_army(self):
        # cheapest army unit costs 50 minerals
        if self.minerals < 50:
            return
        # rebuild lost workers
        if self.larvae and self.supply_workers + self.already_pending(UnitID.DRONE) < 15:
            self.actions.append(self.larvae.first.train(UnitID.DRONE))
        # rebuild lost queen
        if self.units(UnitID.SPAWNINGPOOL).ready and not self.queens and self.units(UnitID.HATCHERY).idle:
            if self.can_afford(UnitID.QUEEN):
                hatch = self.units(UnitID.HATCHERY).first
                self.actions.append(hatch.train(UnitID.QUEEN))
            return
        if self.larvae and self.units(UnitID.ROACHWARREN) and self.units(UnitID.ROACHWARREN).ready:
            if self.can_afford(UnitID.ROACH):
                # note that this only builds one unit per step
                self.actions.append(self.larvae.first.train(UnitID.ROACH))
            # only build zergling if you cant build roach soon
            elif self.minerals >= 50 and self.vespene <= 8:
                self.actions.append(self.larvae.first.train(UnitID.ZERGLING))

    def train_overlords(self):
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
