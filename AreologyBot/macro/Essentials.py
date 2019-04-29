import sc2
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class Essentials:
    async def start_step(self):
        # send a welcome message
        await self.chat_send("(glhf)")
        # split supply_workers
        for drone in self.drones:
            # find closest mineral patch
            closest_mineral_patch = self.state.mineral_field.closest_to(drone)
            self.actions.append(drone.gather(closest_mineral_patch))
        # only do on_step every nth step, 8 is standard
        self._client.game_step = 8
