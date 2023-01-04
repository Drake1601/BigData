import re
import pandas as pd
import scrapy
from scrapy import Selector
from scrapy.http import Request,Response
from ..items import LeagueItem

class LeagueSpider(scrapy.Spider):
    name = 'league'
    allowed_domains = ['fbref.com']
    start_urls = [
        'https://fbref.com/en/comps/12/history/La-Liga-Seasons',
        'https://fbref.com/en/comps/9/history/Premier-League-Seasons',
        'https://fbref.com/en/comps/20/history/Bundesliga-Seasons',
        'https://fbref.com/en/comps/11/history/Serie-A-Seasons',
        'https://fbref.com/en/comps/13/history/Ligue-1-Seasons'
        ]

    def parse(self,response: Response, **kwargs):
        season_list = response.xpath('//table/tbody/tr/td*[@data-stat="year_id"]/a/@href')
        for season in season_list:
            yield Request(
                'https://fbref.com'+season,
                callback = self.parse_season_info()
            )

    def parse_season_info(self,response:Response, **kwargs):
        league_item = LeagueItem(response)
        return league_item