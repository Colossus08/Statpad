import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import json
import bs4
import lxml
import plotly
import scipy.stats
from bs4 import BeautifulSoup
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    print('made the driver')
    return driver


def get_fbref_chrome(driver, url, table_id):
    driver.get(url)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, table_id))
    )
    return driver.page_source  # Return full page source


def getPlayerStats(team_code_list,league_id,csv_name, team_names, league_name,season_id):
    team_counter=0
    # iterating through every team in respective league
    for team in range(len(team_code_list)):
        condition=404
        while condition!=200:
            ps_stats=requests.get(ps,params={'team_id':team_code_list[team],'league_id':league_id,'season_id':season_id},headers=headers)
            condition=ps_stats.status_code
            if condition!=200:
                print('\nrequesting again\n')
        # ps_stats=requests.get(ps,params={'team_id':team_code_list[team],'league_id':league_id,'season_id':season_id},headers=headers)
        # print(ps_stats.status_code,'\n')
        players_stats=ps_stats.json()['players']
        final_players_dict={}
        for count in players_stats:
            if count['meta_data']['player_name']!=None:
                final_players_dict[count['meta_data']['player_name']]={}
                for player in count['stats']:
                    for aspect in count['stats'][player]:
                        final_players_dict[count['meta_data']['player_name']][aspect]=count['stats'][player][aspect]
        for final_player in final_players_dict.keys():
            temp=final_players_dict[final_player]
            temp['name']=final_player
            temp['team']=team_names[team_counter]
            if 'pl_players_df' not in locals():
                pl_players_df=pd.DataFrame(data=temp,index=[0])
                # print(pl_players_df)
            else:
                # pl_players_df.loc[len(pl_players_df)]=temp
                pl_players_df = pd.concat([pl_players_df, pd.DataFrame([temp])], ignore_index=True)
        # name_col=pl_players_df.pop('name')
        # pl_players_df.insert(0,'name',name_col)  
        # pl_players_df = pl_players_df.copy()   
        
        team_counter+=1
    pl_players_df['league']=league_name
    # print(csv_name)
    final_csv_name=re.sub(r'\.',f'_{season_id}.',csv_name)
    # print(final_csv_name)
    pl_players_df.to_csv(f'{final_csv_name}',index=False)
    print(f'saved {final_csv_name}')
    # pl_players_df=None



# getting content from specified url
api_url='https://fbrapi.com/'

# generate api key
api_key_url=api_url+'generate_api_key'
api_key_response=requests.post(api_key_url)
api_key=api_key_response.json()['api_key']
headers={"X-API-Key": api_key}
ps=api_url+'player-season-stats'

driver = init_driver()  # Initialize the driver once

#league meta data containing the url, table_id from which we obtain the team_codes, league_code for the api, and name of the respective league data
league_metadata={'La Liga':{
                    'league_url':'https://fbref.com/en/comps/12/---La-Liga-Stats',
                    'table_id':'results---121_overall',
                    'league_code':12,
                    'csv_name':'la_liga_player_stats.csv'
                },
                'Premier League':{
                    'league_url':'https://fbref.com/en/comps/9/---Premier-League-Stats',
                    'table_id':'results---91_overall',
                    'league_code':9,
                    'csv_name':'premier_league_player_stats.csv'
                },
                'Bundesliga':{
                    'league_url':'https://fbref.com/en/comps/20/---Bundesliga-Stats',
                    'table_id':'results---201_overall',
                    'league_code':20,
                    'csv_name':'bundesliga_player_stats.csv'
                },
                'Ligue 1':{
                    'league_url':'https://fbref.com/en/comps/13/---Ligue-1-Stats',
                    'table_id':'results---131_overall',
                    'league_code':13,
                    'csv_name':'ligue1_player_stats.csv'
                },
                'Serie A':{
                    'league_url':'https://fbref.com/en/comps/11/---Serie-A-Stats',
                    'table_id':'results---111_overall',
                    'league_code':11,
                    'csv_name':'serie_a_player_stats.csv'
                }
            }
# years=['2024-2025','2023-2024','2022-2023','2021-2022','2020-2021','2019-2020','2018-2019']
years=['2011-2012']

# iterating through the different leagues
for count in years:
    for league_name in league_metadata:
        main_url=league_metadata[league_name]['league_url']
        main_url=re.sub('---',f'{count}/{count}-',main_url)
        
        table_id=league_metadata[league_name]['table_id']
        table_id=re.sub('---',f'{count}',table_id)
        
        html_content = get_fbref_chrome(driver, main_url,table_id)
        soup=BeautifulSoup(html_content,'lxml')
        
        table=soup.find('table',{'id':table_id})
        tbody=table.find('tbody')
        rows=tbody.find_all('tr')
        
        # getting all the rows containing the name of the teams and corresponding hyperlinks
        team_links=[x.find('td',{'class':'left'}).find('a') for x in rows]
        # clearer when referring to html code of the site, but basically getting classNames and stuff to scrape name and code of teams
        team_codes=[str(x).split('/')[3] for x in team_links]
        team_names=[str(x).split('>')[1][:-3] for x in team_links]
        # print(count)
        print(team_names,end='\n\n')
        # print(team_codes)
        getPlayerStats(team_codes,league_metadata[league_name]['league_code'],league_metadata[league_name]['csv_name'],team_names,league_name,count)
        # break
        time.sleep(10)
        print('done sleeping',end='\n\n')
driver.quit()