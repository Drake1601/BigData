import re
import pandas as pd

import scrapy
from scrapy import Selector
from scrapy.http import Request, Response

from ..items import PlayerItem

COUNTRY_LIST = [
    '/en/country/players/ENG/England-Football-Players',
    '/en/country/players/POR/Portugal-Football-Players'
]

class PlayerSpider(scrapy.Spider):
    name = 'player'
    allowed_domains = ['fbref.com']
    start_urls = ['https://fbref.com/en/players/country/',]

    def parse(self, response: Response, **kwargs):
        country_list = response.xpath('//*[@class="section_content"]/ul/li/div/div/a/@href').extract()
                
        for country in country_list:
            if country in COUNTRY_LIST:
                yield Request(
                    'https://fbref.com' + country,
                    callback=self.parse_country,
                )

        # TEST
        # yield Request(
        #     'https://fbref.com/en/players/d70ce98e/Lionel-Messi',
        #     callback=self.parse_player_info,
        # )

    def parse_country(self, response: Response, **kwargs):
        player_list = response.xpath('//*[@class="section_content"]/p/a/@href').extract()

        for player in player_list[:10]:
            yield Request(
                'https://fbref.com' + player,
                callback=self.parse_player_info,
            )

    def parse_player_info(self, response: Response, **kwargs):
        player_item = PlayerItem(response)
        return player_item