import random
import sc2, sys
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer, Human
from __init__ import run_ladder_game

# Load bot
from main import AreologyBot
my_bot = sc2.player.Bot(Race.Zerg, AreologyBot())

# Run Simulation
if __name__ == "__main__":
    if "--LadderServer" in sys.argv:
        print ("Starting a ladder game ")
        result, opponentid = run_ladder_game(my_bot)
        print(f"{result} against opponent {opponentid}")
    else:
        print ("Starting a local game ")
        random_map = random.choice(["BlueShiftLE", "CeruleanFallLE", "KairosJunctionLE", "ParaSiteLE", "PortAleksanderLE", "StasisLE", "CyberForestLE", "KingsCoveLE", "NewRepugnancyLE", "YearZeroLE"])

        """
        race:       [0] Random      | [1] Terran    | [2] Protoss   | [3] Zerg      |                   |                   |                   |
        difficulty: [0] Easy        | [1] Medium    | [2] Hard      | [3] V Hard    | [4] Cheat Vision  | [5] Cheat Money   | [6] Cheat Insane  |
        build:      [0] Random      | [1] Rush      | [2] Timing    | [3] Power     | [4] Macro         | [5] Air           |                   |
        """
        race =          [Race.Random,Race.Terran, Race.Protoss, Race.Zerg]
        difficulty =    [Difficulty.Easy, Difficulty.Medium, Difficulty.Hard, Difficulty.VeryHard, Difficulty.CheatVision, Difficulty.CheatMoney, Difficulty.CheatInsane]
        build =         [sc2.AIBuild.RandomBuild, sc2.AIBuild.Rush, sc2.AIBuild.Timing, sc2.AIBuild.Power, sc2.AIBuild.Macro, sc2.AIBuild.Air]
        enemy_bot =     sc2.player.Computer(race[0], difficulty[6], build[0])   # Computer(race, difficulty, build)

        sc2.run_game(sc2.maps.get(random_map), [my_bot, enemy_bot],
        realtime = True, save_replay_as="AreologyBotReplay.SC2Replay")
