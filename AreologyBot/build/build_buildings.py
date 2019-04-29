import sc2
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class build_buildings:

    def build_hatcheries(self):
        self.hatch_limit = self.supply_workers / 15
        self.hatch_count = self.units(UnitID.HATCHERY).amount + self.already_pending(UnitID.HATCHERY)
        # hatcheries cost 300 minerals
        if self.minerals < 300:
            return
        if not self.already_pending(UnitID.HATCHERY) and self.hatch_count < self.hatch_limit:
            position = await self.get_next_expansion()
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.HATCHERY, position))
