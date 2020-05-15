import random
from constants import URL
import requests
import settings

class Seed:
    """Query a random player from the top_n players of a specified league to be the seed"""
    def __init__(self, api_key, top_n=20):
        self.api_key = api_key
        self.top_n = top_n

    def _get_seed_summoner_id(self):
        sorted_queue = requests.get(
            URL.base + URL.top_players,
            headers={'X-Riot-Token': self.api_key},
            params={'page': 1},
        )

        random_player = random.choice(sorted_queue.json()[:self.top_n])
        return random_player.get('summonerId')

    def _get_seed_account_id(self, summoner_id):
        summoner_info = requests.get(
            URL.base + URL.summoner_info.format(**{'summonerId': summoner_id}),
            headers={'X-Riot-Token': self.api_key},
        )

        return summoner_info.json().get('accountId')

    def execute(self):
        seed_summoner_id = self._get_seed_summoner_id()
        return self._get_seed_account_id(seed_summoner_id)
