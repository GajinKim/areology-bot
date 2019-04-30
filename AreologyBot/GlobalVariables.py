import sc2
from sc2.constants import *
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

class GlobalVariables:
    def __init__(self):
        self.buildingVariables()
        self.unitVariables()
        self.miscVariables()

    def buildingVariables(self):
        self.hatcheries =           self.units(UnitTypeId.HATCHERY).amount + self.already_pending(UnitTypeId.HATCHERY)
        self.lairs =                self.units(UnitTypeId.LAIR).amount + self.already_pending(UnitTypeId.LAIR)
        self.hives =                self.units(UnitTypeId.HIVE).amount + self.already_pending(UnitTypeId.HIVE)

        self.extractors =           self.units(UnitTypeId.EXTRACTOR).amount + self.already_pending(UnitTypeId.EXTRACTOR)
        self.spawning_pools =       self.units(UnitTypeId.SPAWNINGPOOL).amount + self.already_pending(UnitTypeId.SPAWNINGPOOL)
        self.baneling_nests =       self.units(UnitTypeId.BANELINGNEST).amount + self.already_pending(UnitTypeId.BANELINGNEST)
        self.evolution_chambers =   self.units(UnitTypeId.EVOLUTIONCHAMBER).amount + self.already_pending(UnitTypeId.EVOLUTIONCHAMBER)
        self.spine_crawlers =       self.units(UnitTypeId.SPINECRAWLER).amount + self.units(UnitTypeId.SPINECRAWLERUPROOTED).amount + self.already_pending(UnitTypeId.SPINECRAWLER)
        self.spore_crawlers =       self.units(UnitTypeId.SPORECRAWLER).amount + self.units(UnitTypeId.SPORECRAWLERUPROOTED).amount + self.already_pending(UnitTypeId.SPORECRAWLER)
        self.roach_warrens =        self.units(UnitTypeId.ROACHWARREN).amount + self.already_pending(UnitTypeId.ROACHWARREN)
        self.hydralisk_dens =       self.units(UnitTypeId.HYDRALISKDEN).amount + self.already_pending(UnitTypeId.HYDRALISKDEN)
        self.lurker_dens =          self.units(UnitTypeId.LURKERDENMP).amount + self.already_pending(UnitTypeId.LURKERDENMP)
        self.infestation_pits =     self.units(UnitTypeId.INFESTATIONPIT).amount + self.already_pending(UnitTypeId.INFESTATIONPIT)
        self.spires =               self.units(UnitTypeId.SPIRE).amount + self.already_pending(UnitTypeId.SPIRE)
        self.ultra_caverns =        self.units(UnitTypeId.ULTRALISKCAVERN).amount + self.already_pending(UnitTypeId.ULTRALISKCAVERN)
        self.greater_spires =       self.units(UnitTypeId.GREATERSPIRE).amount + self.already_pending(UnitTypeId.GREATERSPIRE)

        self.lair_finished =                self.units(UnitTypeId.LAIR).ready
        self.hive_finished =                self.units(UnitTypeId.HIVE).ready
        self.spawning_pool_finished =       self.units(UnitTypeId.SPAWNINGPOOL).ready
        self.baneling_nest_finished =       self.units(UnitTypeId.BANELINGNEST).ready
        self.evolution_chamber_finished =   self.units(UnitTypeId.EVOLUTIONCHAMBER).ready
        self.roach_warren_finished =        self.units(UnitTypeId.ROACHWARREN).ready
        self.hydralisk_den_finished =       self.units(UnitTypeId.HYDRALISKDEN).ready
        self.lurker_den_finished =          self.units(UnitTypeId.LURKERDENMP).ready
        self.infestation_pit_finished =     self.units(UnitTypeId.INFESTATIONPIT).ready
        self.spire_finished =               self.units(UnitTypeId.SPIRE).ready
        self.ultra_cavern_finished =        self.units(UnitTypeId.ULTRALISKCAVERN).ready
        self.greater_spire_finished =       self.units(UnitTypeId.GREATERSPIRE).ready

    def unitVariables(self):
        self.larvae =               self.units(UnitTypeId.LARVA)
        self.drones =               self.units(UnitTypeId.DRONE)
        self.queens =               self.units(UnitTypeId.QUEEN)
        self.zerglings =            self.units(UnitTypeId.ZERGLING)
        self.banelings =            self.units(UnitTypeId.BANELING)
        self.roaches =              self.units(UnitTypeId.ROACH)
        self.ravagers =             self.units(UnitTypeId.RAVAGER)
        self.hydralisks =           self.units(UnitTypeId.HYDRALISK)
        self.lurkers =              self.units(UnitTypeId.LURKER)
        self.infestors =            self.units(UnitTypeId.INFESTOR)
        self.infested_terrans =     self.units(UnitTypeId.INFESTEDTERRAN)
        self.swarm_hosts =          self.units(UnitTypeId.SWARMHOSTMP)
        self.locusts =              self.units(UnitTypeId.LOCUSTMP)
        self.ultralisks =           self.units(UnitTypeId.ULTRALISK)
        self.overlords =            self.units(UnitTypeId.OVERLORD)
        self.overseers =            self.units(UnitTypeId.OVERSEER)
        self.changelings =          self.units(UnitTypeId.CHANGELING)
        self.mutalisks =            self.units(UnitTypeId.MUTALISK)
        self.corruptors =           self.units(UnitTypeId.CORRUPTOR)
        self.vipers =               self.units(UnitTypeId.VIPER)
        self.brood_lords =          self.units(UnitTypeId.BROODLORD)
        self.brood_lings =          self.units(UnitTypeId.BROODLING)

    def miscVariables(self):
        self.from_larva =           {UnitTypeId.DRONE, UnitTypeId.OVERLORD, UnitTypeId.ZERGLING, UnitTypeId.ROACH, UnitTypeId.HYDRALISK, UnitTypeId.INFESTOR, UnitTypeId.SWARMHOSTMP,
                                    UnitTypeId.MUTALISK, UnitTypeId.CORRUPTOR, UnitTypeId.VIPER}
        self.from_drone =           {UnitTypeId.HATCHERY, UnitTypeId.EXTRACTOR, UnitTypeId.SPAWNINGPOOL, UnitTypeId.EVOLUTIONCHAMBER, UnitTypeId.SPINECRAWLER, UnitTypeId.SPORECRAWLER,
                                    UnitTypeId.ROACHWARREN,UnitTypeId.HYDRALISKDEN, UnitTypeId.LURKERDENMP, UnitTypeId.INFESTATIONPIT, UnitTypeId.SPIRE, UnitTypeId.ULTRALISKCAVERN, UnitTypeId.GREATERSPIRE}

        self.armyUnits =            self.units.filter(lambda unit: unit.type_id in {UnitTypeId.ZERGLING, UnitTypeId.ROACH, UnitTypeId.HYDRALISK, UnitTypeId.OVERSEER})
        self.droneSupply =          self.units(UnitTypeId.DRONE).amount + self.already_pending(UnitTypeId.DRONE) + self.units(UnitTypeId.EXTRACTOR).ready.filter(lambda x:x.vespene_contents > 0).amount
        self.armySupply =           self.supply_used - self.droneSupply
