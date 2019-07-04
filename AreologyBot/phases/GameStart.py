import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class GameStart:
    async def worker_split(self):
        for drone in self.drones:
            # find closest mineral patch
            closest_mineral_patch = self.state.mineral_field.closest_to(drone)
            self.actions.append(drone.gather(closest_mineral_patch))
        # only do on_step every nth step, 8 is standard
        self._client.game_step = 8

    async def overlord_scout(self):
        scouting_overlord = self.overlords[0]
        self.actions.append(scouting_overlord.move(self.enemy_start_locations[0]))

    async def greeting(self):
        await self.chat_send("(glhf)")
