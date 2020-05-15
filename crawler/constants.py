import requests

class Constants:
    region = 'br1'
    queue_type = 'RANKED_SOLO_5x5'
    tier = 'DIAMOND'
    division = 'I'
    queue = [400, 420]  # 400: alternate draft, 420: ranked solo
    season = 13


class URL:
    base = 'https://{region}.api.riotgames.com'.format(region=Constants.region)
    top_players = '/lol/league-exp/v4/entries/{queue_type}/{tier}/{division}'.format(**{
        'queue_type': Constants.queue_type,
        'tier': Constants.tier,
        'division': Constants.division,
    })
    summoner_info = '/lol/summoner/v4/summoners/{summonerId}'
    matches_by_account_id = '/lol/match/v4/matchlists/by-account/{accountId}'
    match_details_by_match_id = '/lol/match/v4/matches/{matchId}'
    champions_info = 'https://ddragon.leagueoflegends.com/cdn/10.9.1/data/en_US/champion.json'


class Champion:
    @staticmethod
    def _query_champions_names():
        """Build a dictionary with champion Id as key and its name as value"""
        champions_info = requests.get(URL.champions_info)
        champions_names = {}
        for name, attributes in champions_info.json().get('data').items():
            champions_names[int(attributes.get('key'))] = name
        return champions_names
