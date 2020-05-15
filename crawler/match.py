import random
from constants import URL, Constants
import requests
from auxiliary import join_list_of_dicts_by_key

class Match:
    def __init__(self, api_key, account_id, champions_names, n_matches=10):
        self.api_key = api_key
        self.account_id = account_id
        self.champions_names = champions_names
        self.n_matches = n_matches

    def _get_matches(self):
        """Get last n_matches from player."""
        matches = requests.get(
            URL.base + URL.matches_by_account_id.format(**{'accountId': self.account_id}),
            headers={'X-Riot-Token': self.api_key},
            params={
                'endIndex': self.n_matches,
                'season': Constants.season,
                'plataformId': Constants.region,
                'queue': Constants.queue
            },
        )

        return {
            'status_code': matches.status_code,
            'list_of_matches': matches.json().get('matches')
        }

    def _get_match_details(self, match_id):
        match = requests.get(
            URL.base + URL.match_details_by_match_id.format(**{'matchId': match_id}),
            headers={'X-Riot-Token': self.api_key},
        )

        return match.json()

    @staticmethod
    def _is_invalid_match(match):
        """Filter matches with less than 25 min. ARAM and custom games."""
        try:
            if match.get('gameDuration') < 1500 or \
                    match.get('gameMode') != 'CLASSIC' or \
                    match.get('gameType') != 'MATCHED_GAME':
                return True
            else:
                return False
        except (TypeError, KeyError):
            return True

    def _parse_match(self, match):
        parsed = {}
        
        parsed['gameId'] = match.get('gameId')
        
        first_team = match.get('teams')[0]
        if first_team.get('win') == 'Win':
            if first_team.get('teamId') == 100:
                parsed['winner'] = 'blue'
            else:
                parsed['winner'] = 'red'
        else:
            if first_team.get('teamId') == 100:
                parsed['winner'] = 'red'
            else:
                parsed['winner'] = 'blue'
                
        parsed['blue_team'] = []
        parsed['red_team'] = []
        
        participants = join_list_of_dicts_by_key(
            match.get('participants'),
            match.get('participantIdentities'),
            'participantId',
            'participantId'
        )
            
        for player in participants:
            side = 'blue_team' if player.get('teamId') == 100 else 'red_team'
            
            player_i = {k: v for k, v in player.items() if k in ['participantId', 'championId', 'timeline']}
            
            player_i['role'] = player_i.get('timeline', {}).get('role')
            player_i['lane'] = player_i.get('timeline', {}).get('lane')
            del player_i['timeline']
            
            player_i['championName'] = self.champions_names[player_i['championId']]
            player_i['accountId'] = player.get('player').get('accountId')
            
            parsed[side].append(player_i)

        return parsed

    @staticmethod
    def _get_account_ids_list(parsed_match):
        blue_players = [participant.get('accountId') for participant in parsed_match['blue_team']]
        red_players = [participant.get('accountId') for participant in parsed_match['red_team']]
        players = blue_players
        players.extend(red_players)
        return players

    def execute(self):
        result = self._get_matches()

        status_code = result.get('status_code')
        matches = result.get('list_of_matches')

        if not matches:
            print('[ERROR] Status {}'.format(status_code))
            return {
                'match': None,
                'account_ids': []
            }

        while matches:
            random.shuffle(matches)
            random_match = matches.pop()
            random_match_id = random_match.get('gameId')

            match = self._get_match_details(random_match_id)
        
            if self._is_invalid_match(match):
                print('Invalid match. Retrying...')
                continue
        
            parsed_match = self._parse_match(match)
            account_ids = self._get_account_ids_list(parsed_match)

            return {
                'match': parsed_match,
                'account_ids': account_ids
            }
        
        print('[INFO] Cannot find a valid match')
        return {
            'match': None,
            'account_ids': []
        }
