# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field, Selector
import re
import pandas as pd
import os.path
from os import path
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
        if info[0].xpath('.//@class').extract_first() == 'media-item logo loader':
            info = info[1]
        else:
            info = info[0]
        self.fields['info'] = self.process_info(info)
        leng = len(self.fields['info']['ClubName'])
        club_name = self.fields['info']['ClubName'][9:(leng-5)]
        year = self.fields['info']['ClubName'][:9]
        print('club_name',club_name)
        print('year',year)

        if path.exists('/content/BigData/scrapeData/output/club/'+club_name) == False:
          os.mkdir('/content/BigData/scrapeData/output/club/'+club_name)
        if path.exists('/content/BigData/scrapeData/output/club/'+club_name+'/std_stats') == False:
          os.mkdir('/content/BigData/scrapeData/output/club/'+club_name +'/std_stats')
        if path.exists('/content/BigData/scrapeData/output/club/'+club_name+'/scores_fixture') == False:
          os.mkdir('/content/BigData/scrapeData/output/club/'+club_name +'/scores_fixture')
        if path.exists('/content/BigData/scrapeData/output/club/'+club_name+'/shooting') == False:
          os.mkdir('/content/BigData/scrapeData/output/club/'+club_name +'/shooting')
        if path.exists('/content/BigData/scrapeData/output/club/'+club_name+'/passing') == False:
          os.mkdir('/content/BigData/scrapeData/output/club/'+club_name +'/passing')
        if path.exists('/content/BigData/scrapeData/output/club/'+club_name+'/gca') == False:
          os.mkdir('/content/BigData/scrapeData/output/club/'+club_name +'/gca')
        if path.exists('/content/BigData/scrapeData/output/club/'+club_name+'/playtime') == False:
          os.mkdir('/content/BigData/scrapeData/output/club/'+club_name +'/playtime')

        

        # SHOOTING STATS
        shooting_stats_table = response.xpath('//*[@id="stats_shooting_12"] | //*[@id="stats_shooting_11"] | //*[@id="stats_shooting_13"] | //*[@id="stats_shooting_9"] | //*[@id="stats_shooting_20"]')
        print('checkshooting',shooting_stats_table)
        self.fields['shooting_stats'] = self.process_stats_table(shooting_stats_table, f'output/club/'+club_name+'/shooting/'+year+'.csv')

        # PASSING STATS
        passing_stats_table = response.xpath('//*[@id="stats_passing_12"] | //*[@id="stats_passing_11"] | //*[@id="stats_passing_13"] | //*[@id="stats_passing_9"] | //*[@id="stats_passing_20"]')
        print('checkpassing',passing_stats_table)
        self.fields['passing_stats'] = self.process_stats_table(passing_stats_table, f'output/club/'+club_name+'/passing/'+year+'.csv')

        #GOAL AND SHOT CREATION
        gca_table = response.xpath('//*[@id="stats_gca_12"] | //*[@id="stats_gca_11"] | //*[@id="stats_gca_13"] | //*[@id="stats_gca_9"] | //*[@id="stats_gca_20"]')
        print('checkgca',gca_table)
        self.fields['gca_stats'] = self.process_stats_table(gca_table, f'output/club/'+club_name+'/gca/'+year+'.csv')

        #PLAY TIME
        play_time_table = response.xpath('//*[@id="stats_playing_time_12"] | //*[@id="stats_playing_time_9"] | //*[@id="stats_playing_time_11"] | //*[@id="stats_playing_time_13"] | //*[@id="stats_playing_time_20"]')
        print('checkplay',play_time_table)
        self.fields['playtime_stats'] = self.process_stats_table(play_time_table, f'output/club/'+club_name+'/playtime/'+year+'.csv')

        std_stats_table = response.xpath('//*[@id="stats_standard_12"] | //*[@id="stats_standard_11"] | //*[@id="stats_standard_13"] | //*[@id="stats_standard_9"] | //*[@id="stats_standard_20"]')
        print('checkstd',std_stats_table)
        self.fields['std_stats'] = self.process_stats_table(std_stats_table, f'output/club/'+club_name+'/std_stats/'+year+'.csv')

        scores_fixture_table = response.xpath('//*[@id="match_logs_for"]')
        print('checkscore',scores_fixture_table)
        self.field['scores_fixture'] = self.process_stats_table(scores_fixture_table, f'output/club/'+club_name+'/scores_fixture/'+year+'.csv')


    def process_info(self,info:Selector):
        print('info',info)
        clubname = info.xpath('.//h1/span/text()').extract()
        print('clubname',clubname)
        # print(type(leaguename[0]))
        s = clubname[0]
        s = re.sub('\s+', '', s)
        print('s',s)
        # leaguename = 'Laliga'
        return {
            'ClubName': s,
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
                    data[headers[idx]] = (text)
                else:
                    data[headers[idx]] = cell.xpath('.//text()').extract_first()     
            all_data.append(data)

        df = pd.DataFrame(all_data)
        df.to_csv(table_name)
        return df

class LeagueItem(scrapy.Item):
    info = Field()


    def __init__(self,response):

        info = response.xpath('//*[@id="meta"]/div')
        if info[0].xpath('.//@class').extract_first() == 'media-item logo loader':
            info = info[1]
        else:
            info = info[0]
        # print('info',info)
        self.fields['info'] = self.process_info(info)
        leng = len(self.fields['info']['LeagueName'])
        league_name = self.fields['info']['LeagueName'][9:(leng-5)]
        year = self.fields['info']['LeagueName'][:9]
        tmp = "results"+year+"121_overall"
        print(tmp)
        
        
        # regular_season_table = response.xpath(f'//*[@id={tmp}]')
        # print('checkkk',regular_season_table)
        # self.fields['regular_season'] = self.process_stats_table(regular_season_table,f'output/league/'+league_name+'/regular_season/'+year+'.csv')

        # SHOOTING STATS
        shooting_stats_table = response.xpath('//*[@id="stats_squads_shooting_for"]')
        print('checkshooting',shooting_stats_table)
        self.fields['shooting_stats'] = self.process_stats_table(shooting_stats_table, f'output/league/'+league_name+'/shooting/'+year+'.csv')

        #PASSING STATS
        passing_stats_table = response.xpath('//*[@id="stats_squads_passing_for"]')
        print('checkpassing',passing_stats_table)
        self.fields['passing_stats'] = self.process_stats_table(passing_stats_table, f'output/league/'+league_name+'/passing/'+year+'.csv')

        #GOAL AND SHOT CREATION
        gca_table = response.xpath('//*[@id="stats_squads_gca_for"]')
        print('checkgca',gca_table)
        self.fields['gca_stats'] = self.process_stats_table(gca_table, f'output/league/'+league_name+'/gca/'+year+'.csv')

        #PLAY TIME
        play_time_table = response.xpath('//*[@id="stats_squads_playing_time_for"]')
        print('checkplay',play_time_table)
        self.fields['playtime_stats'] = self.process_stats_table(play_time_table, f'output/league/'+league_name+'/playtime/'+year+'.csv')

        squad_stats_table = response.xpath('//*[@id="stats_squads_standard_for"]')
        print(squad_stats_table)
        self.fields['squad_stats'] = self.process_stats_table(squad_stats_table, f'output/league/'+league_name+'/std_stats/'+year+'.csv')

        squad_goalkeeping_table = response.xpath('//*[@id="stats_squads_keeper_for"]')
        print(squad_goalkeeping_table)
        self.field['squad_goal_keeping'] = self.process_stats_table(squad_goalkeeping_table, f'output/league/'+league_name+'/goalkeeping/'+year+'.csv')

        #PLAY TIME
        play_time_table = response.xpath('//*[@id="stats_squads_playing_time_for"]')
        print('checkplay',play_time_table)
        self.fields['playtime_stats'] = self.process_stats_table(play_time_table, f'output/league/'+league_name+'/playtime/'+year+'.csv')


    def process_info(self,info:Selector):
        print('info',info)
        leaguename = info.xpath('.//h1/text()').extract()
        print('leaguename',leaguename)
        # print(type(leaguename[0]))
        s = leaguename[0]
        s = re.sub('\s+', '', s)
        # leaguename = 'Laliga'
        return {
            'LeagueName': s,
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
                    data[headers[idx]] = (text)
                else:
                    data[headers[idx]] = cell.xpath('.//text()').extract_first()     
            all_data.append(data)

        df = pd.DataFrame(all_data)
        df.to_csv(table_name)
        return df
