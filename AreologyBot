import random
import math

from sc2.unit import *
from sc2.units import *
from sc2.data import *

import sc2
from sc2 import Race, Difficulty, maps, run_game
from sc2.constants import *
from sc2.ids.ability_id import *
from sc2.ids.unit_typeid import *
from sc2.ids.upgrade_id import *
from sc2.position import Point2, Point3
from sc2.player import Bot, Computer, Human

# note: self.townhalls.amount = number of hatcheries + lairs + hives
# note: foo.exists (can be buildling)
# note: bar.ready (is already finished)

""" ### To do-List [Ctrl + f "###" to see problematic places]

### Need to order this list into most important to least

Implement Scouting
Implement Early game defense
Implement Immediate gas saturation
Implement Creep spread (and tumor placement)
Implement Proper army manipulation (army distribution), don't make them just sit in main
Implement Anti cloak measues
Implement Check all enemy bases
Implement Proper extractor production (ERRORS)
Implement Overseer logic (builds way too many)
Implement Burrow Micro
Implement Queen Inject
Implement No conga line all attack

Need to fix Evolution Chamber upgrade logic (sometimes 2nd evo doesn't work)
"""
class AreologyBot(sc2.BotAI):
    def __init__(self):
        # PRODUCTION BOOLEANS
        self.allowArmyProduction = []
        self.allowDroneProduction = []
        self.allowQueenProduction = []

        ### Need to implement later
        self.defenseTriggerRange = 30

        # major events
        self.lairStarted = False
        self.hiveStarted = False
        self.greaterspireStarted = False
        self.burrowUpgradeStarted = False

    # Total time elapsed (in minutes)
    def minutesElapsed(self):
        return self.time / 60

    async def on_step(self, iteration):
        """

        """
        # on_step Intializations
        # Note: used frequently for building, upgrade, and production prioritizations
        self.allowArmyProduction = [True]
        self.allowDroneProduction = [True]
        self.allowQueenProduction = [True] # Only used when building Lair and Hive

        self.allowQueenInject = [True]
        self.allowQueenCreepTumor = [True]

        """
        Variable Initializations is reinitialized each iteration
        """
        # Actual Drone Count (existing + in production + in gas)
        self.actualDroneCount = self.units(DRONE).amount + self.already_pending(DRONE) + self.units(EXTRACTOR).ready.filter(lambda x:x.vespene_contents > 0).amount

        # Actual Unit Count (existing + in production)
        self.actualOverlordCount = self.units(OVERLORD).amount + self.already_pending(OVERLORD)
        self.actualQueenCount = self.units(QUEEN).amount + self.already_pending(QUEEN)
        self.actualLingCount = self.units(ZERGLING).amount + self.already_pending(ZERGLING)
        self.actualRoachCount = self.units(ROACH).amount + self.already_pending(ROACH)
        self.actualHydraCount = self.units(HYDRALISK).amount + self.already_pending(HYDRALISK)
        self.actualCorruptorCount = self.units(CORRUPTOR).amount + self.already_pending(CORRUPTOR)
        self.actualBroodlordCount = self.units(BROODLORD).amount + self.units(BROODLORDCOCOON).amount

        # Actual Army Count (All units except Drones, Overlords, and Queens)
        self.actualArmyCount = self.actualLingCount + self.actualRoachCount + self.actualHydraCount + self.actualCorruptorCount + self.actualBroodlordCount

        ### Need to implement gas prioritization
        await self.distribute_workers()

        """
        BUILD ORDER (HATCH FIRST)
        """
        # Start Drone Immediately
        # Note: also accounts for sub 13 supply, in case of going under
        if self.actualDroneCount < 13 and self.can_afford(DRONE) and self.supply_left >= 1 and self.units(LARVA).exists:
            await self.do(self.units(LARVA).random.train(DRONE))

        # Start Second Overlord on 13
        if self.actualDroneCount == 13 and not self.already_pending(OVERLORD) and self.supply_used < 200 and self.units(LARVA).exists:
            self.allowDroneProduction.append(False)
            if self.can_afford(OVERLORD):
                await self.do(self.units(LARVA).random.train(OVERLORD))

        # Start Spawning Pool on 17
        # Note: Second Hatchery and Extractor must have already been started
        if self.actualDroneCount == 17 and self.units(DRONE).exists and self.units(EXTRACTOR).amount >= 1 and self.townhalls.amount >= 2:
            if self.units(SPAWNINGPOOL).amount + self.already_pending(SPAWNINGPOOL) < 1:
                self.allowDroneProduction.append(False)
                self.allowArmyProduction.append(False)
                if self.can_afford(SPAWNINGPOOL):
                    await self.build(SPAWNINGPOOL, near = self.townhalls.first.position.towards(self.game_info.map_center, 5))

        # Start Third Overlord on 20
        if self.actualDroneCount == 20 and not self.already_pending(OVERLORD) and self.supply_used < 200 and self.units(LARVA).exists:
            self.allowDroneProduction.append(False)
            if self.can_afford(OVERLORD):
                await self.do(self.units(LARVA).random.train(OVERLORD))

            # Start Zerglings once Spawning Pool is finished
            if all(self.allowArmyProduction) and self.units(SPAWNINGPOOL).ready and self.actualLingCount < 2 and self.units(LARVA).exists and self.supply_left >= 2:
                self.allowDroneProduction.append(False)
                if self.can_afford(ZERGLING):
                    await self.do(self.units(LARVA).random.train(ZERGLING))
        """""""""""""""
             MACRO
           OVERLORDS
        """""""""""""""
        # Overlord Start Conditions (More than 3 Overlords)
        # At least 3 overlords finished
        if self.units(LARVA).exists and self.supply_cap < 200 and self.supply_left <= 8 and self.units(OVERLORD).ready.amount >= 3:
            if self.already_pending(OVERLORD) == 0:
                self.allowQueenProduction.append(False)
                self.allowDroneProduction.append(False)
                self.allowArmyProduction.append(False)
                if self.can_afford(OVERLORD):
                    await self.do(self.units(LARVA).random.train(OVERLORD))
            elif self.supply_left <= 4 and self.already_pending(OVERLORD) == 1:
                self.allowQueenProduction.append(False)
                self.allowDroneProduction.append(False)
                self.allowArmyProduction.append(False)
                if self.can_afford(OVERLORD):
                    await self.do(self.units(LARVA).random.train(OVERLORD))
        """""""""""""""
             MACRO
           EXPANDING
        """""""""""""""
        if self.minutesElapsed() >= 6 and self.supply_used >= 140 and self.townhalls.ready.amount >= 3:     self.townhallsLimit = 8
        elif self.minutesElapsed() >= 5 and self.actualDroneCount >= 35 and self.townhalls.amount == 3:     self.townhallsLimit = 4
        elif self.actualDroneCount >= 29 and self.actualQueenCount >= 2 and self.townhalls.amount == 2:     self.townhallsLimit = 3
        elif self.actualDroneCount >= 17:                                                                   self.townhallsLimit = 2
        else:                                                                                               self.townhallsLimit = 1

        if self.townhalls.amount < self.townhallsLimit and self.units(DRONE).exists:
            if not self.already_pending(HATCHERY):
                self.allowArmyProduction.append(False)
                self.allowDroneProduction.append(False)
                self.allowQueenProduction.append(False)
                if self.can_afford(HATCHERY):
                    await self.expand_now()
            elif self.already_pending(HATCHERY) == 1 and self.townhallsLimit == 8 and self.minerals > 750:
                await self.expand_now()
        """""""""""""""
             MACRO
           EXTRACTOR
        """""""""""""""
        if self.townhalls.amount >= 4 and self.actualDroneCount >= 66:            self.extractorLimit = self.townhalls.ready.amount * 2
        elif self.townhalls.amount >= 2 and self.units(ROACHWARREN).exists:       self.extractorLimit = 3
        elif self.townhalls.amount >= 2 and self.actualDroneCount >= 17:          self.extractorLimit = 1
        else:                                                                     self.extractorLimit = 0

        for townhall in self.townhalls.ready:
            considered_vespene = self.state.vespene_geyser.closer_than(10.0, townhall)
            for target_vespene in considered_vespene:
                drone = self.select_build_worker(target_vespene.position)
                if drone is None or target_vespene is None:
                    break
                if self.units(EXTRACTOR).amount + self.already_pending(EXTRACTOR) < self.extractorLimit:
                    self.allowDroneProduction.append(False)
                    if self.can_afford(EXTRACTOR):
                        await self.do(drone.build(EXTRACTOR, target_vespene))
                        break
        """""""""""""""
             MACRO
           BUILDINGS
        """""""""""""""
        # Roach Warren at 44 Drones
        # At least 44 drones and Spawning Pool is finished
        if self.units(DRONE).exists and self.actualDroneCount >= 44 and self.units(SPAWNINGPOOL).ready and self.townhalls.exists:
            if self.units(ROACHWARREN).amount + self.already_pending(ROACHWARREN) < 1:
                self.allowArmyProduction.append(False)
                self.allowDroneProduction.append(False)
                if self.can_afford(ROACHWARREN):
                    await self.build(ROACHWARREN, near = self.units(HATCHERY).first.position.towards(self.game_info.map_center, 5))

        # Evolution Chamber(s) Start Conditions
        # At least 50 drones, roach warren exists, and at least 3 townhalls
        if self.units(DRONE).exists and self.actualDroneCount >= 50 and self.townhalls.amount >= 3 and self.units(ROACHWARREN).exists:
            if self.units(EVOLUTIONCHAMBER).amount + self.already_pending(EVOLUTIONCHAMBER) < 2:
                self.allowDroneProduction.append(False)
                self.allowArmyProduction.append(False)
                if self.minerals > 150:
                    await self.build(EVOLUTIONCHAMBER, near = self.units(HATCHERY).first.position.towards(self.game_info.map_center, 5))

        # Start Lair no sooner than 5:30
        if self.units(HATCHERY).ready.idle.exists and self.minutesElapsed() >= 5.5 and self.actualDroneCount >= 50 and self.units(SPAWNINGPOOL).ready and self.townhalls.amount >= 3:
            if not self.lairStarted:
                self.allowArmyProduction.append(False)
                self.allowDroneProduction.append(False)
                self.allowQueenProduction.append(False)
                if self.can_afford(LAIR):
                    await self.do(self.units(HATCHERY).ready.idle.random(UPGRADETOLAIR_LAIR))
                    self.lairStarted = True

        # Start Hydralisk Den immediatley after Lair finishes
        if self.units(DRONE).exists and self.units(LAIR).ready.exists:
            if self.units(HYDRALISKDEN).amount + self.already_pending(HYDRALISKDEN) < 1:
                self.allowDroneProduction.append(False)
                self.allowArmyProduction.append(False)
                if self.can_afford(HYDRALISKDEN):
                    await self.build(HYDRALISKDEN, near = self.units(HATCHERY).first.position.towards(self.game_info.map_center, 5))

        # Infestation Pit Start Conditions
        # Lair is finished, at least 50 drones, at least 4 townhalls, and at least 6:00
        if self.units(DRONE).exists and self.units(LAIR).ready and self.minutesElapsed() > 6 and self.actualDroneCount >= 55 and self.townhalls.amount >= 4:
            if self.units(INFESTATIONPIT).amount + self.already_pending(INFESTATIONPIT) < 1 and self.units(HYDRALISK).ready:
                self.allowDroneProduction.append(False)
                self.allowArmyProduction.append(False)
                if self.can_afford(INFESTATIONPIT):
                    await self.build(INFESTATIONPIT, near = self.units(HATCHERY).first.position.towards(self.game_info.map_center, 5))

        # Start Spire after reaching 150 supply off 4 mining bases
        if self.units(DRONE).exists and (self.units(LAIR).ready or self.units(HIVE).ready) and self.minutesElapsed() > 7 and self.supply_used >= 180 and self.townhalls.amount >= 5:
            if self.units(SPIRE).amount + self.already_pending(SPIRE) < 1:
                self.allowDroneProduction.append(False)
                self.allowArmyProduction.append(False)
                if self.can_afford(SPIRE):
                    await self.build(SPIRE, near = self.units(HATCHERY).first.position.towards(self.game_info.map_center, 5))

        # Start Hive no sooner than 8:00
        if self.units(LAIR).ready.idle.exists and self.minutesElapsed() > 8 and self.supply_used >= 180 and self.units(INFESTATIONPIT).ready and self.units(SPIRE).exists and self.townhalls.amount >=5:
            if not self.hiveStarted:
                self.allowArmyProduction.append(False)
                self.allowDroneProduction.append(False)
                self.allowQueenProduction.append(False)
                if self.can_afford(HIVE):
                    await self.do(self.units(LAIR).ready.idle.random(UPGRADETOHIVE_HIVE))
                    self.hiveStarted = True

        # Start Greater Spire immediately after hive is finished
        if self.units(HIVE).ready and self.units(SPIRE).ready.idle.exists:
            if not self.greaterspireStarted:
                self.allowArmyProduction.append(False)
                self.allowDroneProduction.append(False)
                self.allowQueenProduction.append(False)
                if self.can_afford(GREATERSPIRE):
                    await self.do(self.units(SPIRE).ready.idle.random(UPGRADETOGREATERSPIRE_GREATERSPIRE))
                    self.greaterspireStarted = True
        """""""""""""""
             MACRO
            UPGRADE
        """""""""""""""
        # Research Metabolic Boost and Adrenal Glands
        if self.units(SPAWNINGPOOL).ready:
            for spawning_pool in self.units(SPAWNINGPOOL).ready.noqueue:
                available_zergling_upgrades = await self.get_available_abilities(spawning_pool)
                important_zergling_upgrades = [AbilityId.RESEARCH_ZERGLINGMETABOLICBOOST, AbilityId.RESEARCH_ZERGLINGADRENALGLANDS]
                for ability in important_zergling_upgrades:
                    if ability in available_zergling_upgrades:
                        self.allowDroneProduction.append(False)
                        self.allowArmyProduction.append(False)
                        if self.can_afford(ability):
                            await self.do(spawning_pool(ability))

        # Research Glial Regeneration (technically Reconstitution) and Tunneling Claws
        if self.units(ROACHWARREN).ready and self.units(LAIR).ready:
            for roach_warren in self.units(ROACHWARREN).ready.noqueue:
                available_roach_upgrades = await self.get_available_abilities(roach_warren)
                important_roach_upgrades = [AbilityId.RESEARCH_GLIALREGENERATION, AbilityId.RESEARCH_TUNNELINGCLAWS]
                for ability in important_roach_upgrades:
                    if ability in available_roach_upgrades:
                        self.allowDroneProduction.append(False)
                        self.allowArmyProduction.append(False)
                        if self.can_afford(ability):
                            await self.do(roach_warren(ability))

        # Research Muscular Augments and Grooved Spines
        if self.units(HYDRALISKDEN).ready:
            for hydralisk_den in self.units(HYDRALISKDEN).ready.noqueue:
                available_hydra_upgrades = await self.get_available_abilities(hydralisk_den)
                important_hydra_upgrades = [AbilityId.RESEARCH_MUSCULARAUGMENTS, AbilityId.RESEARCH_GROOVEDSPINES]
                for ability in important_hydra_upgrades:
                    if ability in available_hydra_upgrades:
                        self.allowDroneProduction.append(False)
                        self.allowArmyProduction.append(False)
                        if self.can_afford(ability):
                            await self.do(hydralisk_den(ability))

        # Research Missile and Armor Upgrades immediately after Evolution Chambers finish
        ### Add in melee upgrades too once hive finishes
        if self.units(EVOLUTIONCHAMBER).ready:
            for evolution_chamber in self.units(EVOLUTIONCHAMBER).ready.noqueue:
                available_evolution_upgrades = await self.get_available_abilities(evolution_chamber)
                important_evolution_upgrades = [AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2, \
                AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1, \
                AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL3]
                for ability in important_evolution_upgrades:
                    if ability in available_evolution_upgrades:
                        self.allowDroneProduction.append(False)
                        self.allowArmyProduction.append(False)
                        if self.can_afford(ability):
                            await self.do(evolution_chamber(ability))

        # Research Burrow after 4 townhalls
        if not self.burrowUpgradeStarted and self.townhalls.ready.amount >= 4:
            for hatch in self.units(HATCHERY).ready.noqueue:
                abilities = await self.get_available_abilities(hatch)
                if AbilityId.RESEARCH_BURROW in abilities:
                    self.allowArmyProduction.append(False)
                    self.allowDroneProduction.append(False)
                    self.allowQueenProduction.append(False)
                    if self.can_afford(AbilityId.RESEARCH_BURROW):
                        await self.do(hatch(AbilityId.RESEARCH_BURROW))
                        self.burrowUpgradeStarted = True
        """""""""""""""
            TEMPORARY
        ATTACK ALGORITHM
        """""""""""""""
        # Defend if less than 170 supply
        if self.supply_used < 170:
            defensive_units = {ZERGLING: [1], ROACH: [1], HYDRALISK: [1], OVERSEER: [1], BROODLORD: [1], QUEEN: [1]}
            for defenseforce in defensive_units:
                for defensesquad in self.units(defenseforce).idle:
                    await self.do(defensesquad.attack(self.townhalls.first.position.towards(self.game_info.map_center, 5)))

        # Attack if at least 170 supply
        elif self.supply_used >= 170:
            aggressive_units = {ZERGLING: [1], ROACH: [1], HYDRALISK: [1], OVERSEER: [1], BROODLORD: [1]}
            for attackforce in aggressive_units:
                for attacksquad in self.units(attackforce).idle:
                    await self.do(attacksquad.attack(self.enemy_start_locations[0]))
        """
        Note:
        Queen Spells (Exclusivity Ordering: Transfuse > Creep Tumor > Inject)

        Are near the bottom of each iteration to enable
        """

        """
        Queen Spells
        # Needs Fixing
        """
        if self.allowQueenInject:
            for queen in self.units(QUEEN).idle:
                abilities = await self.get_available_abilities(queen)
                for hatchery in self.townhalls.ready:
                    if AbilityId.EFFECT_INJECTLARVA in abilities:
                        if not hatchery.has_buff(BuffId.QUEENSPAWNLARVATIMER):
                            await self.do(queen(AbilityId.EFFECT_INJECTLARVA, hatchery))
                            break
        """""""""""""""
        UNIT PRODUCTION AT END OF ITERATION
        FOR UPGRADE/BUILDING PRIORITIZATION
        """""""""""""""

        """""""""""""""
             MACRO
            DRONING
        """""""""""""""
        if self.townhalls.ready.amount >= 4: self.droneLimit = 90
        else:                                self.droneLimit = 66

        if all(self.allowDroneProduction) and self.actualDroneCount < self.droneLimit and self.supply_left >= 1 and self.units(LARVA).exists and self.actualDroneCount < 22 * self.townhalls.ready.amount:
            if self.can_afford(DRONE):
                if self.actualDroneCount < 3 * (self.actualArmyCount + self.actualQueenCount) or not self.units(ROACHWARREN).ready:
                    await self.do(self.units(LARVA).random.train(DRONE))
        """""""""""""""
             MACRO
        QUEEN PRODUCTION
        """""""""""""""
        if self.townhalls.ready.amount >= 5:   self.queenlimit = 7
        elif self.townhalls.ready.amount >= 3: self.queenLimit = 5
        else:                                  self.queenLimit = 3

        # Early Game Queen Production Conditions
        # Spawning Pool exists and fewer than 2 or fewer townhalls are ready
        if all(self.allowQueenProduction) and self.townhalls.ready.amount <= 2 and self.units(SPAWNINGPOOL).ready and self.supply_left >= 2 and self.actualQueenCount < self.queenLimit:
            for hatch in self.units(HATCHERY).ready.noqueue:
                self.allowDroneProduction.append(False)
                self.allowArmyProduction.append(False)
                if self.can_afford(QUEEN):
                    await self.do(hatch.train(QUEEN))

        """""""""""""""
             MACRO
           ARMY UNIT
        """""""""""""""
        # Start Zerglings once Spawning Pool is finished
        if all(self.allowArmyProduction) and self.units(SPAWNINGPOOL).ready and self.actualLingCount < 8 and self.units(LARVA).exists and not self.units(ROACHWARREN).ready and self.supply_left >= 1:
            if self.can_afford(ZERGLING):
                await self.do(self.units(LARVA).random.train(ZERGLING))

        # Start Roaches once Roach Warren is finished
        if all(self.allowArmyProduction) and self.units(ROACHWARREN).ready and self.can_afford(ROACH) and self.units(LARVA).exists:
            # Hydralisk Den and Greater spire are both not finished
            if not self.units(HYDRALISKDEN).ready and not self.units(GREATERSPIRE).ready:
                await self.do(self.units(LARVA).random.train(ROACH))
            # Hydralisk Den is finished but Greater Spire is not
            elif self.units(HYDRALISKDEN).ready and not self.units(GREATERSPIRE).ready:
                if self.actualRoachCount < 1.5 * self.actualHydraCount:
                    await self.do(self.units(LARVA).random.train(ROACH))
            # Hydralisk Den and Greater Spire are both finished (Don't produce past 170 - Save room for Broodlords)
            elif self.units(HYDRALISKDEN).ready and self.units(GREATERSPIRE).ready and self.supply_used < 170:
                if self.actualRoachCount < 0.75 * self.actualHydraCount:
                    await self.do(self.units(LARVA).random.train(ROACH))

        # Start Hydralisks once Hydralisk Den is finished
        if all(self.allowArmyProduction) and self.units(HYDRALISKDEN).ready and self.can_afford(HYDRALISK) and self.units(LARVA).exists:
            # Greater Spire is not finished
            if not self.units(GREATERSPIRE).ready:
                await self.do(self.units(LARVA).random.train(HYDRALISK))
            # Greater Spire is finished (Don't produce past 170 - Save room for Broodlords)
            elif self.units(GREATERSPIRE).ready and self.supply_left < 170:
                    await self.do(self.units(LARVA).random.train(HYDRALISK))

        # Corrupter Production Conditions
        # Greater Spire is finished and number of corrupters + broodlords is fewer than 7
        if all(self.allowArmyProduction) and self.units(GREATERSPIRE).ready and self.actualCorruptorCount + self.actualBroodlordCount < 7 and self.units(LARVA).exists:
            if self.can_afford(CORRUPTOR) and self.supply_left >= 2:
                await self.do(self.units(LARVA).random.train(CORRUPTOR))

        # Broodlord Production Conditions
        # Greater Spire is finished and a corrupter is ready (idle)
        if all(self.allowArmyProduction) and self.units(GREATERSPIRE).ready and self.units(CORRUPTOR).idle.exists and self.supply_left >= 2 and self.units(LARVA).exists:
            if self.can_afford(BROODLORD):
                LowestHealthIdleCorrupter = min(self.units(CORRUPTOR), key=lambda x:x.health)
                await self.do(LowestHealthIdleCorrupter(MORPHTOBROODLORD_BROODLORD))
"""""""""""""""
    TESTING
"""""""""""""""
def main():
    # [0] Terran | [1] Protoss | [2] Zerg | [3] Random
    # [0] Easy | [1] Medium | [2] Hard | [3] Elite | [4] Cheat Vision | [5] Cheat Money | [6] Cheat Insane
    COMPUTER_RACE = [Race.Terran, Race.Protoss, Race.Zerg, Race.Random]
    COMPUTER_DIFFICULTY = [Difficulty.Easy, Difficulty.Medium, Difficulty.Hard, Difficulty.VeryHard, Difficulty.CheatVision, Difficulty.CheatMoney, Difficulty.CheatInsane]

    sc2.run_game(maps.get("BlueShiftLE"), [
        Bot(Race.Zerg, AreologyBot()),
        Computer(COMPUTER_RACE[3], COMPUTER_DIFFICULTY[3])
    ], realtime = False)

if __name__ == '__main__':
    main()
