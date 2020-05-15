import settings
from seed import Seed
from constants import Champion
from match import Match
from time import sleep, time
import random
import gc
import os
import pickle
from datetime import datetime

class Crawler:
    def __init__(self):
        self.api_key = settings.API_KEY
        self.PATH = 'crawler/matches/'
        self.SIZE = 10000
        self.STACK_SIZE = 50
        self.CHUNK_SIZE = 500
        self.COUNTER = 0
        self.viewed_matches = []
        self.stack_accounts = []
        self.matches = []

    def _get_seed_account_id(self):
        seed = Seed(self.api_key)
        return seed.execute()

    def _save_matches(self):
        with open(self.PATH + 'matches_' + datetime.strftime(datetime.now(), '%Y%m%d%H%M%S') + '.pickle', 'wb') as file:
            pickle.dump(self.matches, file)
        
    def _load_matches(self):
        matches = []
        files = [f for f in os.listdir(self.PATH) if f.endswith('.pickle')]
        for f in files:
            with open(self.PATH + f, 'rb') as pkl:
                m = pickle.load(pkl)
            matches.extend(m)
        
        return matches

    def _load_previous_results(self):
        """Fill viewed_matches with previous results"""
        matches = self._load_matches()
        game_ids = [match.get('gameId') for match in matches]
        self.viewed_matches.extend(game_ids)
        return

    def execute(self):
        print('Loading previous results')
        self._load_previous_results()

        print('Getting seed')
        seed_account_id = self._get_seed_account_id()
        champions_names = Champion._query_champions_names()
        match = Match(self.api_key, seed_account_id, champions_names, 10)
        result = match.execute()

        print('Successfully got seed account\n')

        self.viewed_matches.append(result['match'].get('gameId'))
        self.stack_accounts.extend(result['account_ids'])
        self.matches.append(result['match'])

        print('Beginning to crawl\n')

        while self.stack_accounts:
            start_time = time()
            
            random.shuffle(self.stack_accounts)
            account_id = self.stack_accounts.pop()

            print('accountId {}'.format(account_id))
            
            match = Match(self.api_key, account_id, champions_names, 10)
            result = match.execute()

            if not result['match']:
                print()
                continue

            match_id = result['match'].get('gameId')

            print('gameId {}'.format(match_id))

            if match_id in self.viewed_matches:
                print('[INFO] Already parsed this match\n')
                continue

            self.COUNTER += 1

            self.matches.append(result['match'])
            self.viewed_matches.append(match_id)

            print('Buffer size: {} matches '.format(len(self.matches)))

            if len(self.stack_accounts) < self.STACK_SIZE:
                self.stack_accounts.extend(result['account_ids'])
                print('[INFO] Extending stack to {} Ids'.format(len(self.stack_accounts)))

            if len(self.matches) > self.CHUNK_SIZE:
                print('[INFO] Saving matches to pickle')
                self._save_matches()
                self.matches = []

            if self.COUNTER > self.SIZE:
                break

            if self.COUNTER % 10 == 0:
                print('[INFO] Parsed {} games'.format(self.COUNTER))
            
            print('{:.2f}s seconds elapsed'.format(time() - start_time))
            print()

            gc.collect()

        self._save_matches()

        return

if __name__ == "__main__":
    crawler = Crawler()
    result = crawler.execute()
