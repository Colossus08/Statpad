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
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options

api_url='https://fbrapi.com/'

def get_fbref_firefox(url):
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no window)
    options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass bot detection

    # Install & set up GeckoDriver for Firefox
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    # Open the URL
    driver.get(url)
    driver.implicitly_wait(10)  # Wait for JavaScript to load

    # Get full page source
    html = driver.page_source
    driver.quit()

    return html

def getPlayerStats(team_code_list,league_id,csv_name):
    team_counter=1
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
            if 'pl_players_df' not in locals():
                pl_players_df=pd.DataFrame(data=temp,index=[0])
                # print(pl_players_df)
            else:
                pl_players_df.loc[len(pl_players_df)]=temp
        name_col=pl_players_df.pop('name')
        pl_players_df.insert(0,'name',name_col)     
        
        team_counter+=1
    pl_players_df.to_csv(f'{csv_name}',index=False)



# getting content from specified url
main_url = "https://fbref.com/en/comps/12/La-Liga-Stats"
html_content = get_fbref_firefox(main_url)


soup=BeautifulSoup(html_content,'lxml')
table=soup.find('table',{'id':'results2024-2025121_overall'})
tbody=table.find('tbody')
rows=tbody.find_all('tr')
team_links=[x.find('td',{'class':'left'}).find('a') for x in rows]
team_codes=[str(x).split('/')[3] for x in team_links]

api_key_url=api_url+'generate_api_key'
api_key_response=requests.post(api_key_url)
api_key=api_key_response.json()['api_key']

headers={"X-API-Key": api_key}
ps=api_url+'player-season-stats'

getPlayerStats(team_codes,12,'la_liga_player_stats.csv')
