import re
import pandas as pd

import scrapy
from scrapy import Selector
from scrapy.http import Request, Response

from ..items import ClubItem

class ClubSpider(scrapy.Spider):
    name = 'club'
    allowed_domains = ['fbref.com']
    start_urls = [
        'https://fbref.com/en/comps/12/history/La-Liga-Seasons',
        'https://fbref.com/en/comps/9/history/Premier-League-Seasons',
        'https://fbref.com/en/comps/20/history/Bundesliga-Seasons',
        'https://fbref.com/en/comps/11/history/Serie-A-Seasons',
        'https://fbref.com/en/comps/13/history/Ligue-1-Seasons'
        ]
    
    def parse(self,response: Response, **kwargs):
        league_list = response.xpath('//table/tbody/tr/td*[@data-stat="year_id"]/a/@href').extract()
        for league in league_list:
            yield Request(
                'https://fbref.com'+league,
                callback = self.parse_club
            )

    def parse_club(self,response: Response, **kwargs):
        club_list = response.xpath('//table/tbody/tr/td*[@data-stat="team"]/a/@href').extract()

        for club in club_list:
            yield Request(
                'https://fbref.com' + club,
                callback = self.parse_club_info,
            )

    def parse_club_info(self,response: Response, **kwargs):
        club_item = ClubItem(response)
        return club_item