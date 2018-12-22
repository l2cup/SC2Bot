import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2_bot import SCIIBot

run_game(maps.get("AbyssalReefLE"), [Bot(Race.Protoss, SCIIBot()), Computer(
    Race.Terran, Difficulty.Medium)], realtime=False)
