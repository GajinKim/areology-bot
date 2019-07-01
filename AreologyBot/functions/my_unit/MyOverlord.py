import sc2
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class MyOverlord:
    async def sendScout(self):
        scouting_overlord = self.overlords[0]
        self.actions.append(scouting_overlord.move(self.enemy_start_locations[0]))

    async def retreatScout(self):
        for overlord in self.units(UnitID.OVERLORD):
            damaged_overlord = overlord.health < 200
            if damaged_overlord:
                # damaged overlord sent back home
                self.actions.append(overlord.move(self.units(UnitID.HATCHERY).first.position))