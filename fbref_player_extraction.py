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

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    print('made the driver')
    return driver


def get_fbref_firefox(driver, url):
    """Fetch the HTML source using an existing WebDriver instance."""
    driver.get(url)
    return driver.page_source  # Return full page source


def getPlayerStats(team_code_list,league_id,csv_name, team_names, league_name):
    team_counter=0
    
    # iterating through every team in respective league
    for team in range(len(team_code_list)):
        ps_stats=requests.get(ps,params={'team_id':team_code_list[team],'league_id':league_id},headers=headers)
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
    pl_players_df.to_csv(f'{csv_name}',index=False)
    print(f'saved {csv_name}')
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
                    'league_url':'https://fbref.com/en/comps/12/La-Liga-Stats',
                    'table_id':'results2024-2025121_overall',
                    'league_code':12,
                    'csv_name':'la_liga_player_stats.csv'
                },
                'Premier League':{
                    'league_url':'https://fbref.com/en/comps/9/Premier-League-Stats',
                    'table_id':'results2024-202591_overall',
                    'league_code':9,
                    'csv_name':'premier_league_player_stats.csv'
                },
                'Bundesliga':{
                    'league_url':'https://fbref.com/en/comps/20/Bundesliga-Stats',
                    'table_id':'results2024-2025201_overall',
                    'league_code':20,
                    'csv_name':'bundesliga_player_stats.csv'
                },
                'Ligue 1':{
                    'league_url':'https://fbref.com/en/comps/13/Ligue-1-Stats',
                    'table_id':'results2024-2025131_overall',
                    'league_code':13,
                    'csv_name':'ligue1_player_stats.csv'
                },
                'Serie A':{
                    'league_url':'https://fbref.com/en/comps/11/Serie-A-Stats',
                    'table_id':'results2024-2025111_overall',
                    'league_code':11,
                    'csv_name':'serie_a_player_stats.csv'
                }
            }

# iterating through the different leagues
for count in league_metadata:
    print(f'{count}')
    main_url = league_metadata[count]['league_url']  
    print(main_url)  
    # html_content = get_fbref_firefox(main_url)
    html_content = get_fbref_firefox(driver, main_url)
    
    # finding the table from the league_url, and searching for the team_code in the hyperlink url
    soup=BeautifulSoup(html_content,'lxml')
    table=soup.find('table',{'id':league_metadata[count]['table_id']})
    tbody=table.find('tbody')
    rows=tbody.find_all('tr')
    
    # getting all the rows containing the name of the teams and corresponding hyperlinks
    team_links=[x.find('td',{'class':'left'}).find('a') for x in rows]
    # clearer when referring to html code of the site, but basically getting classNames and stuff to scrape name and code of teams
    team_codes=[str(x).split('/')[3] for x in team_links]
    team_names=[str(x).split('>')[1][:-3] for x in team_links]
    
    getPlayerStats(team_codes,league_metadata[count]['league_code'],league_metadata[count]['csv_name'],team_names,count)
    
driver.quit()