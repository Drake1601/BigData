# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field, Selector

import pandas as pd

from .utils import writeFile

class PlayerItem(scrapy.Item):
    info = Field()
    std_stats = Field()

    def __init__(self, response):
        # INFO
        info = response.xpath('//*[@id="meta"]/div')
        if info[0].xpath('.//@class').extract_first() == 'media-item':
            info = info[1]
        else:
            info = info[0]
        self.fields['info'] = self.process_info(info)
        
        # STANDARD STATS
        std_stats_table = response.xpath('//*[@id="stats_standard_dom_lg"]')
        self.fields['std_stats'] = self.process_stats_table(std_stats_table, f'output/std/std_'+self.fields['info']['ShortName']+'.csv')

        # SHOOTING STATS
        shooting_stats_table = response.xpath('//*[@id="stats_shooting_dom_lg"]')
        self.fields['shooting_stats'] = self.process_stats_table(shooting_stats_table, f'output/shooting/shooting_'+self.fields['info']['ShortName']+'.csv')

        # PASSING STATS
        passing_stats_table = response.xpath('//*[@id="stats_passing_dom_lg"]')
        self.fields['passing_stats'] = self.process_stats_table(passing_stats_table, f'output/passing/passing_'+self.fields['info']['ShortName']+'.csv')


    def process_info(self, info: Selector):
        shortname = info.xpath('.//h1/span/text()').extract_first()
        
        hasfullname = 0
        fullname = None

        print(info.xpath('.//p[0]/span/text()').extract_first())
        if info.xpath('.//p[0]/span/text()').extract_first() != 'Position:':
            hasfullname = 1
            fullname = info.xpath('.//p[0]/span/text()').extract_first()
        
        position = info.xpath(f'.//p[{hasfullname}]/text()').extract()
        writeFile(position)

        return {
            'ShortName': shortname,
            'FullName': fullname,
        }

    def process_stats_table(self, table, table_name):
        if not table:
            return None
            
        headers = table.xpath('.//thead/tr[last()]/th/text()').extract()
        rows = table.xpath('.//tbody/tr[@id="stats"]')

        all_data = []
        for row in rows:
            cells = row.xpath('.//th|.//td')
            data = {}
            for idx, cell in enumerate(cells):
                if cell.xpath('.//@class').extract_first() in ['thead', 'over_header thead']:
                    print(cell.xpath('.//text()').extract_first())
                    continue
                if cell.xpath('.//a').extract_first():
                    text = cell.xpath('.//a/text()').extract_first()
                    href = cell.xpath('.//a/@href').extract_first()
                    data[headers[idx]] = (text, href)
                else:
                    data[headers[idx]] = cell.xpath('.//text()').extract_first()     
            all_data.append(data)

        df = pd.DataFrame(all_data)
        df.to_csv(table_name)
        return df

class ClubItem(scrapy.Item):
    info = Field()
    std_stats = Field()
    
    def __init__(self,response):

        info = response.xpath('//*[@id="meta"]/div')
        if info[0].xpath('.//@class').extract_first() == 'media-item logo':
            info = info[1]
        else:
            info = info[0]
        self.fields['info'] = self.process_info(info)

        std_stats_table = response.xpath('//*[@id="stats_standard_12"]')
        self.fields['std_stats'] = self.process_stats_table(std_stats_table, f'output/club/std/std_'+self.fields['info']['ClubName']+'.csv')

        scores_fixture_table = response.xpath('//*[@id="match_logs_for"]')
        self.field['scores_fixture'] = self.process_stats_table(scores_fixture_table, f'output/club/match_logs/match_logs_'+self.fields['info']['ClubName']+'.csv')

        # SHOOTING STATS
        shooting_stats_table = response.xpath('//*[@id="stats_shooting_12"]')
        self.fields['shooting_stats'] = self.process_stats_table(shooting_stats_table, f'output/club/shooting/shooting_'+self.fields['info']['ClubName']+'.csv')

        # PASSING STATS
        passing_stats_table = response.xpath('//*[@id="stats_passing_12"]')
        self.fields['passing_stats'] = self.process_stats_table(passing_stats_table, f'output/club/passing/passing_'+self.fields['info']['ClubName']+'.csv')

        #GOAL AND SHOT CREATION
        gca_table = response.xpath('//*[@id="stats_gca_12"]')
        self.fields['gca_stats'] = self.process_stats_table(gca_table, f'output/club/gca/gca_'+self.fields['info']['ClubName']+'.csv')

        #PLAY TIME
        play_time_table = response.xpath('//*[@id="stats_playing_time_12"]')
        self.fields['playtime_stats'] = self.process_stats_table(play_time_table, f'output/club/playtime/playtime_'+self.fields['info']['ClubName']+'.csv')


    def process_info(self,info:Selector):
        clubname = info.xpath('.//h1/span/text()').extract_first()
        print(clubname)
    
        return {
            'ClubName': clubname,
        }

    def process_stats_table(self, table, table_name):
        if not table:
            return None
            
        headers = table.xpath('.//thead/tr[last()]/th/text()').extract()
        rows = table.xpath('.//tbody/tr')

        all_data = []
        for row in rows:
            cells = row.xpath('.//th|.//td')
            data = {}
            for idx, cell in enumerate(cells):
                if cell.xpath('.//@class').extract_first() in ['thead', 'over_header thead']:
                    print(cell.xpath('.//text()').extract_first())
                    continue
                if cell.xpath('.//a').extract_first():
                    text = cell.xpath('.//a/text()').extract_first()
                    href = cell.xpath('.//a/@href').extract_first()
                    data[headers[idx]] = (text, href)
                else:
                    data[headers[idx]] = cell.xpath('.//text()').extract_first()     
            all_data.append(data)

        df = pd.DataFrame(all_data)
        df.to_csv(table_name)
        return df

    class LeagueItem(scrapy.Spider):
        info = Field()


        def __init__(self,response):

            info = response.xpath('//*[@id="meta"]/div')
            if info[0].xpath('.//@class').extract_first() == 'media-item logo':
                info = info[1]
            else:
                info = info[0]
            self.fields['info'] = self.process_info(info)

            regular_season_table = response.xpath('//*[class="stats_table sortable min_width force_mobilize now_sortable sticky_table eq2 re2 le2"]')
            self.fields['regular_season'] = self.process_stats_table(regular_season_table,f'output/league/regular_season/'+self.fields['info']['LeagueName']+'.csv')

            squad_stats_table = response.xpath('//*[@id="stats_squads_standard_for"]')
            self.fields['squad_stats'] = self.process_stats_table(squad_stats_table, f'output/league/std/std_'+self.fields['info']['LeagueName']+'.csv')

            squad_goalkeeping_table = response.xpath('//*[@id="stats_squads_keeper_for"]')
            self.field['squad_goal_keeping'] = self.process_stats_table(squad_goalkeeping_table, f'output/league/goalkeeping/'+self.fields['info']['ShortName']+'.csv')

            # SHOOTING STATS
            shooting_stats_table = response.xpath('//*[@id="stats_squads_shooting_for"]')
            self.fields['shooting_stats'] = self.process_stats_table(shooting_stats_table, f'output/league/shooting/shooting_'+self.fields['info']['ShortName']+'.csv')

            # PASSING STATS
            passing_stats_table = response.xpath('//*[@id="stats_squads_passing_for"]')
            self.fields['passing_stats'] = self.process_stats_table(passing_stats_table, f'output/league/passing/passing_'+self.fields['info']['ShortName']+'.csv')

            #GOAL AND SHOT CREATION
            gca_table = response.xpath('//*[@id="stats_squads_gca_for"]')
            self.fields['gca_stats'] = self.process_stats_table(gca_table, f'output/league/gca/gca_'+self.fields['info']['ShortName']+'.csv')

            #PLAY TIME
            play_time_table = response.xpath('//*[@id="stats_squads_playing_time_for"]')
            self.fields['playtime_stats'] = self.process_stats_table(play_time_table, f'output/league/playtime/playtime_'+self.fields['info']['ShortName']+'.csv')


        def process_info(self,info:Selector):
            leaguename = info.xpath('.//h1/text()').extract_first()
            # print(clubname) 
            return {
                'LeagueName': leaguename,
            }

        def process_stats_table(self, table, table_name):
            if not table:
                return None
                
            headers = table.xpath('.//thead/tr[last()]/th/text()').extract()
            rows = table.xpath('.//tbody/tr')

            all_data = []
            for row in rows:
                cells = row.xpath('.//th|.//td')
                data = {}
                for idx, cell in enumerate(cells):
                    if cell.xpath('.//@class').extract_first() in ['thead', 'over_header thead']:
                        print(cell.xpath('.//text()').extract_first())
                        continue
                    if cell.xpath('.//a').extract_first():
                        text = cell.xpath('.//a/text()').extract_first()
                        href = cell.xpath('.//a/@href').extract_first()
                        data[headers[idx]] = (text, href)
                    else:
                        data[headers[idx]] = cell.xpath('.//text()').extract_first()     
                all_data.append(data)

            df = pd.DataFrame(all_data)
            df.to_csv(table_name)
            return df
