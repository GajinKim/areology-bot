import sc2
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class train_units:
    def build_army(self):
        # we cant build any army unit with less than 50 minerals
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

    def build_overlords(self):
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
