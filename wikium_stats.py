import json

import requests
from cached_property import cached_property
from parsel import Selector


class WikiumStats:
    GAME_STAT_URL = 'https://wikium.ru/statistic/_comparation_game_data/{}'
    HEADERS = {
        'Host': 'wikium.ru',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Referer': 'https://wikium.ru/train',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    def __init__(self, creds):
        self.creds = creds

    @cached_property
    def headers(self):
        headers = self.HEADERS.copy()
        headers['Cookie'] = self.cookies
        return headers

    @cached_property
    def cookies(self):
        response = requests.post('https://wikium.ru/login', headers=self.HEADERS, data=self.creds)
        return response.history[0].headers['Set-Cookie']

    @cached_property
    def user_data(self):
        response = requests.get('https://wikium.ru/statistic/today', headers=self.headers)
        sel = Selector(text=response.text)
        return json.loads(sel.re_first(r'carrotquest\.identify\((.*?)\);'))

    @cached_property
    def skill_groups(self):
        response = requests.get('https://wikium.ru/games', headers=self.headers)
        sel = Selector(text=response.text)

        skill_groups = []
        for elem in sel.css('.games-content__group'):
            skill_group = {}
            skill_group['title'] = elem.css('.games-content__group-title::text').extract_first()
            skill_group['skill_code'] = elem.css('::attr(data-skill)').extract_first()
            skill_group['bpi'] = self.user_data['current_bpi_' + skill_group['skill_code']]
            skill_group['games'] = []

            game_codes = elem.css('.game-preview__link::attr(href)').re(r'/game/(.*)')
            for game_code in game_codes:
                url = self.GAME_STAT_URL.format(game_code)
                game_data = requests.get(url, headers=self.headers).json()['game_data']
                if game_data['bpi'] is not None:
                    game_data['bpi'] = round(float(game_data['bpi']))
                skill_group['games'].append(game_data)

            skill_groups.append(skill_group)

        return skill_groups
