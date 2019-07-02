import sc2
from sc2.constants import *
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

class GlobalVariables:
    def __init__(self):
        self.building_variables()
        self.unit_variables()
        self.misc_variables()

    def building_variables(self):
        self.hatcheries =                   self.units(UnitTypeId.HATCHERY)
        self.lairs =                        self.units(UnitTypeId.LAIR)
        self.hives =                        self.units(UnitTypeId.HIVE)
        self.extractors =                   self.units(UnitTypeId.EXTRACTOR)
        self.spawning_pools =               self.units(UnitTypeId.SPAWNINGPOOL)
        self.baneling_nests =               self.units(UnitTypeId.BANELINGNEST)
        self.evolution_chambers =           self.units(UnitTypeId.EVOLUTIONCHAMBER)
        self.spine_crawlers =               self.units(UnitTypeId.SPINECRAWLER)
        self.spore_crawlers =               self.units(UnitTypeId.SPORECRAWLER)
        self.roach_warrens =                self.units(UnitTypeId.ROACHWARREN)
        self.hydralisk_dens =               self.units(UnitTypeId.HYDRALISKDEN)
        self.lurker_dens =                  self.units(UnitTypeId.LURKERDENMP)
        self.infestation_pits =             self.units(UnitTypeId.INFESTATIONPIT)
        self.spires =                       self.units(UnitTypeId.SPIRE)
        self.ultra_caverns =                self.units(UnitTypeId.ULTRALISKCAVERN)
        self.greater_spires =               self.units(UnitTypeId.GREATERSPIRE)

        self.hatchery_finished =            self.units(UnitTypeId.HATCHERY).ready
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

    def unit_variables(self):
        # Hatch Tech
        self.larvae =                       self.units(UnitTypeId.LARVA)
        self.drones =                       self.units(UnitTypeId.DRONE)
        self.overlords =                    self.units(UnitTypeId.OVERLORD)
        self.queens =                       self.units(UnitTypeId.QUEEN)
        self.zerglings =                    self.units(UnitTypeId.ZERGLING)
        self.banelings =                    self.units(UnitTypeId.BANELING)
        self.roaches =                      self.units(UnitTypeId.ROACH)
        self.ravagers =                     self.units(UnitTypeId.RAVAGER)
        # Lair Tech
        self.hydralisks =                   self.units(UnitTypeId.HYDRALISK)
        self.lurkers =                      self.units(UnitTypeId.LURKER)
        self.overseers =                    self.units(UnitTypeId.OVERSEER)
        self.changelings =                  self.units(UnitTypeId.CHANGELING)
        self.corruptors =                   self.units(UnitTypeId.CORRUPTOR)
        self.swarm_hosts =                  self.units(UnitTypeId.SWARMHOSTMP)
        self.locusts =                      self.units(UnitTypeId.LOCUSTMP)
        self.infestors =                    self.units(UnitTypeId.INFESTOR)
        self.infested_terrans =             self.units(UnitTypeId.INFESTEDTERRAN)
        self.mutalisks =                    self.units(UnitTypeId.MUTALISK)
        # Hive Tech
        self.vipers =                       self.units(UnitTypeId.VIPER)
        self.ultralisks =                   self.units(UnitTypeId.ULTRALISK)
        self.brood_lords =                  self.units(UnitTypeId.BROODLORD)
        self.brood_lings =                  self.units(UnitTypeId.BROODLING)

    def upgrade_variables(self):
        # Evolution Chamber Upgrades
        self.melee_attacks_1 =              AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL1
        self.melee_attacks_2 =              AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2
        self.melee_attacks_3 =              AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3
        self.missile_attacks_1 =            AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1
        self.missile_attacks_2 =            AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2
        self.missile_attacks_3 =            AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL3
        self.ground_armor_1 =               AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1
        self.ground_armor_2 =               AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2
        self.ground_armor_3 =               AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3
        # Spire Upgrades
        self.flyer_attacks_1 =              AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL1
        self.flyer_attacks_2 =              AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL2
        self.flyer_attacks_3 =              AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL3
        self.flyer_armor_1 =                AbilityId.RESEARCH_ZERGFLYERARMORLEVEL1
        self.flyer_armor_2 =                AbilityId.RESEARCH_ZERGFLYERARMORLEVEL2
        self.flyer_armor_3 =                AbilityId.RESEARCH_ZERGFLYERARMORLEVEL3
        # Hatchery Upgrades
        self.overlord_speed =               AbilityId.RESEARCH_PNEUMATIZEDCARAPACE
        self.burrow =                       AbilityId.RESEARCH_BURROW
        # Spawning Pool Upgrades
        self.ling_speed =                   AbilityId.RESEARCH_ZERGLINGMETABOLICBOOST
        self.adrenal_glandes =              AbilityId.RESEARCH_ZERGLINGADRENALGLANDS
        # Baneling Nest Upgrades
        self.bane_speed =                   AbilityId.RESEARCH_CENTRIFUGALHOOKS
        # Roach Warren Upgrades
        self.roach_speed =                  AbilityId.RESEARCH_GLIALREGENERATION
        self.tunneling_claws =              AbilityId.RESEARCH_TUNNELINGCLAWS
        # Hydralisk Den Upgrades
        self.hydra_speed =                  AbilityId.RESEARCH_MUSCULARAUGMENTS
        self.hydra_range =                  AbilityId.RESEARCH_GROOVEDSPINES
        # Infestation Pit Upgrades
        self.neural_parasite =              AbilityId.RESEARCH_NEURALPARASITE
        # Ultralisk Cavern Upgrades
        self.ultralisk_armor =              AbilityId.RESEARCH_CHITINOUSPLATING

    def misc_variables(self):
        self.from_larva =                   {UnitTypeId.DRONE, UnitTypeId.OVERLORD, UnitTypeId.ZERGLING, UnitTypeId.ROACH, UnitTypeId.HYDRALISK, UnitTypeId.INFESTOR, UnitTypeId.SWARMHOSTMP,
                                            UnitTypeId.MUTALISK, UnitTypeId.CORRUPTOR, UnitTypeId.VIPER}
        self.from_drone =                   {UnitTypeId.HATCHERY, UnitTypeId.EXTRACTOR, UnitTypeId.SPAWNINGPOOL, UnitTypeId.EVOLUTIONCHAMBER, UnitTypeId.SPINECRAWLER, UnitTypeId.SPORECRAWLER,
                                            UnitTypeId.ROACHWARREN,UnitTypeId.HYDRALISKDEN, UnitTypeId.LURKERDENMP, UnitTypeId.INFESTATIONPIT, UnitTypeId.SPIRE, UnitTypeId.ULTRALISKCAVERN, UnitTypeId.GREATERSPIRE}

        self.army_units =                   self.units.filter(lambda unit: unit.type_id in {UnitTypeId.ZERGLING, UnitTypeId.ROACH, UnitTypeId.HYDRALISK, UnitTypeId.OVERSEER})
        self.worker_supply =                self.units(UnitTypeId.DRONE).amount + self.already_pending(UnitTypeId.DRONE) + self.units(UnitTypeId.EXTRACTOR).ready.filter(lambda x:x.vespene_contents > 0).amount
        self.army_supply =                  self.supply_used - self.worker_supply
