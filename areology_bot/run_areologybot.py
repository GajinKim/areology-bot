
class AreologyBot()

def main():
    COMPUTER_RACE = [Race.Terran, Race.Protoss, Race.Zerg, Race.Random]
    COMPUTER_DIFFICULTY = [Difficulty.Easy, Difficulty.Medium, Difficulty.Hard, Difficulty.VeryHard, Difficulty.CheatVision, Difficulty.CheatMoney, Difficulty.CheatInsane]

    sc2.run_game(maps.get("CyberForestLE"), [
        Bot(Race.Zerg, AreologyBot()),
        Computer(COMPUTER_RACE[3], COMPUTER_DIFFICULTY[3])
    ], realtime = False, save_replay_as="AreologyBot.SC2Replay")

if __name__ == '__main__':
    main()
