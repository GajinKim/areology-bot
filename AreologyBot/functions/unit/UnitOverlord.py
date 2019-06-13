import sc2
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class UnitOverlord:
    # sends overlord to scout build order phase
    async def sendScout(self):
        for overlord in self.units(UnitID.OVERLORD):
            overlord_damaged = overlord.health < 150
            if not overlord_damaged:
                # non damaged overlord moves towards enemy main
                self.actions.append(overlord.attack(self.enemy_start_locations[0]))

    # retreat back home if health is under 125 hp
    async def tacticalRetreat(self):
        for overlord in self.units(UnitID.OVERLORD):
            overlord_damaged = overlord.health < 150
            if (overlord_damaged):
                # damaged overlord sent back home
                self.actions.append(overlord.attack(self.units(UnitID.HATCHERY).first.position))
