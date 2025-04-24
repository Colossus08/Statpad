import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from streamlit_card import card
from streamlit_searchbox import st_searchbox
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.neighbors import NearestNeighbors

st.set_page_config(
    page_title="Player Comparison",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# initialise the players to be compared
if 'player1' not in st.session_state:
    st.session_state.player1=''
if 'player2' not in st.session_state:
    st.session_state.player2=''
if 'player1_pos' not in st.session_state:
    st.session_state.player1_pos=''
if 'player2_pos' not in st.session_state:
    st.session_state.player2_pos=''
if 'positions_similar_to_a' not in st.session_state:
    st.session_state.positions_similar_to_a=[]
if 'positions_similar_to_b' not in st.session_state:
    st.session_state.positions_similar_to_b=[]
if 'graph_player_selection' not in st.session_state:
    st.session_state.graph_player_selection=st.session_state.player1



df=pd.read_csv('../databases_maybe/premier_league_player_stats.csv')
df2=pd.read_csv('../databases_maybe/la_liga_player_stats.csv')
df3=pd.read_csv('../databases_maybe/bundesliga_player_stats.csv')
df4=pd.read_csv('../databases_maybe/serie_a_player_stats.csv')
df5=pd.read_csv('../databases_maybe/ligue1_player_stats.csv')

final_df=pd.concat([df,df2,df3,df4,df5],ignore_index=True)

def search_player(searchterm: str) -> list:
    return [item for item in final_df['name'] if searchterm.lower() in item.lower()]

def update_player_name(playerName1,playerName2):
    st.session_state.player1=playerName1 
    st.session_state.player1_pos=final_df[final_df['name']==f'{st.session_state.player1}']['positions'].iloc[0].split(',')[0]
    st.session_state.player2=playerName2
    st.session_state.player2_pos=final_df[final_df['name']==f'{st.session_state.player2}']['positions'].iloc[0].split(',')[0]
        # else:
        #     st.session_state.player1=playerName1
        # if 'player2' not in st.session_state:
        #     st.session_state.player2=playerName2
        # else:
        #     st.session_state.player2=playerName2


with st.sidebar:
    st.title('Player Comparison')
 
    player1_name = st_searchbox(
    search_player,
    placeholder="Search Player ",
    key="player1_select"
    )
    
    player2_name = st_searchbox(
    search_player,
    placeholder="Search Player ",
    key="player2_select"
    )
    
    st.button('submit',on_click=update_player_name,args=(player1_name,player2_name))


st.text(f'{st.session_state.player1}: {st.session_state.player1_pos}')
st.text(f'{st.session_state.player2}: {st.session_state.player2_pos}')



# option to choose features for comparison
with st.container(border=True):
    col1,col2,col3,col4=st.columns(4)
    feature1=col1.selectbox(
        "Feature 1",
        final_df.columns[1:-3]
    )

    feature2=col2.selectbox(
        "Feature 2",
        final_df.columns[1:-3]
    )

    feature3=col3.selectbox(
        "Feature 3",
        final_df.columns[1:-3]
    )

    feature4=col4.selectbox(
        "Feature 4",
        final_df.columns[1:-3]
    )

# creating radar chart
categories = ['progressive passes','key passes','live pass leading to shot','take on leading to shot','goal creation actions']

if (st.session_state.player1!='' and st.session_state.player2!=''):
    
    player_a=final_df[final_df['name']==f'{st.session_state.player1}'][[feature1,feature2,feature3,feature4]].iloc[0]
    
    player_b=final_df[final_df['name']==f'{st.session_state.player2}'][[feature1,feature2,feature3,feature4]].iloc[0]
    
    val_max=max([player_a.max(),player_b.max()])
    
    
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=player_a,
        theta=[feature1,feature2,feature3,feature4],
        fill='toself',
        name=f'{st.session_state.player1}'
    ))
    fig.add_trace(go.Scatterpolar(
        r=player_b,
        theta=[feature1,feature2,feature3,feature4],
        fill='toself',
        name=f'{st.session_state.player2}',
        line=dict(
            color='red',
        )
    ))

    fig.update_layout(
    polar=dict(
        bgcolor='#1e2130',
        radialaxis=dict(
        visible=True,
        range=[0,val_max+10]
        )),
    showlegend=True
    )

    st.plotly_chart(fig)
else:
    st.title('Use sidebar to select players to compare')


st.divider()

if (st.session_state.player1!='' and st.session_state.player2!=''):
    
    # percentile_df=final_df.copy()
    # single_position_column=percentile_df['positions'].to_list()
    # for count in range(len(single_position_column)):
    #     single_position_column[count]=single_position_column[count].split(',')[0]
    #     print(single_position_column[count])
    # percentile_df['positions']=single_position_column
    
    # player_a_percentile_df=percentile_df.loc[percentile_df['positions']==st.session_state.player1_pos]
    # player_b_percentile_df=percentile_df.loc[percentile_df['positions']==st.session_state.player2_pos]
    
    
    # st.dataframe(player_a_percentile_df)
    
    # percentile_ranks_a = [stats.percentileofscore(player_a_percentile_df[feature1], player_a[feature1], kind='rank'),stats.percentileofscore(player_a_percentile_df[feature2], player_a[feature2], kind='rank'),stats.percentileofscore(player_a_percentile_df[feature3], player_a[feature3], kind='rank'),stats.percentileofscore(player_a_percentile_df[feature4], player_a[feature4], kind='rank')]
    # percentile_ranks_b = [stats.percentileofscore(player_b_percentile_df[feature1], player_b[feature1], kind='rank'),stats.percentileofscore(player_b_percentile_df[feature2], player_b[feature2], kind='rank'),stats.percentileofscore(player_b_percentile_df[feature3], player_b[feature3], kind='rank'),stats.percentileofscore(player_b_percentile_df[feature4], player_b[feature4], kind='rank')]
    # percentile_ranks_max = [stats.percentileofscore(player_a_percentile_df[feature1],player_a_percentile_df[feature1].max() , kind='rank'),stats.percentileofscore(player_a_percentile_df[feature2],player_a_percentile_df[feature2].max(), kind='rank'),stats.percentileofscore(player_a_percentile_df[feature3], player_a_percentile_df[feature3].max(), kind='rank'),stats.percentileofscore(player_a_percentile_df[feature4], player_a_percentile_df[feature4].max(), kind='rank')]
    
    
    # fig = go.Figure()
    
    # x=[feature1,feature2,feature3,feature4]

    # fig.add_trace(go.Bar(name='Highest percentile', x=x, y=percentile_ranks_max))
    # fig.add_trace(go.Bar(name=f'{st.session_state.player1}', x=x, y=percentile_ranks_a))
    # fig.update_layout(barmode='overlay')
    
    
    # # fig.add_trace()
    # # fig=px.bar(final_df,x=[1,2,3,4],y=percentile_ranks_max)
    
    # st.plotly_chart(fig)
    
    # create df to store only single position
    single_position_column=final_df['positions'].to_list()
    for count in range(len(single_position_column)):
        single_position_column[count]=single_position_column[count].split(',')[0]
        # print(single_position_column[count])
    final_df['positions']=single_position_column
    
    
    ##### Calculating similar players now
    
    def similarPlayers(playerPosition,playerName,featureList):
        tempdf=final_df[final_df['positions']==f'{playerPosition}'].fillna(0)
        tempdf['SNo']=tempdf.index
        
        required=tempdf[tempdf['name']==f'{playerName}']

        float_cols = tempdf.drop(columns=['SNo']).select_dtypes(include=['float64','int64']).columns.tolist()
        transformer = ColumnTransformer(
        transformers=[
                ('scale', StandardScaler(), float_cols)
            ],
            remainder='passthrough'  # Leave other columns untouched
        )
        
        print(playerName)
        
        transformed = transformer.fit_transform(tempdf)
        new_columns = float_cols + [col for col in tempdf.columns if col not in float_cols]
        df_transformed = pd.DataFrame(transformed, columns=new_columns)
        # df_transformed=df_transformed[df_transformed.columns[::-1]]
        
        # required=df_transformed[df_transformed['name']==f'{playerName}']
        
        df_transformed=df_transformed[df_transformed['name']!=f'{playerName}']
        
        
        nbrs = NearestNeighbors(n_neighbors=11,metric='cosine').fit(tempdf.drop(columns=['SNo','name','team','league','positions'])[featureList])
        distances, indices = nbrs.kneighbors(required.drop(columns=['SNo','name','positions','team','league'])[featureList])
        
        # print(indices[0])
        
        print("Nearest neighbors (points):", tempdf.iloc[indices[0]])
        
        mostSimilarPlayers=tempdf.iloc[indices[0][1:]]
        # targetPlayer=tempdf.iloc[indices[0][0]]
        
        return mostSimilarPlayers[mostSimilarPlayers.columns[::-1]][['name','team','positions']+featureList+['league']]
    
    
    featureList=[]
    if feature1 not in featureList:
        featureList.append(feature1)
    if feature2 not in featureList:
        featureList.append(feature2)
    if feature3 not in featureList:
        featureList.append(feature3)
    if feature4 not in featureList:
        featureList.append(feature4)
        
    
    similar1,similar2=st.columns(2)
    
    player1Similar=similarPlayers(st.session_state.player1_pos,st.session_state.player1,featureList)
    
    similar1.text(f'{st.session_state.player1}:')
    # st.dataframe(player1Similar[0])
    similar1.dataframe(final_df[final_df['name']==st.session_state.player1][['name','team','positions']+featureList+['league']].reset_index(drop=True))
    
    similar1.text('Similar Players:')
    similar1.dataframe(player1Similar.reset_index(drop=True))
    
    
    
    player2Similar=similarPlayers(st.session_state.player2_pos,st.session_state.player2,featureList)
    
    similar2.text(f'{st.session_state.player2}:')
    # st.dataframe(player1Similar[0])
    similar2.dataframe(final_df[final_df['name']==st.session_state.player2][['name','team','positions']+featureList+['league']].reset_index(drop=True))
    
    similar2.text('Similar Players:')
    similar2.dataframe(player2Similar.reset_index(drop=True))
    
    
    # create df to filter out only selected player position
    # singling out the selected player to be used for KNN
#     temp=final_df[final_df['positions']=='FW'].fillna(0)
#     required=temp[temp['name']=='Harry Kane']
    
#     float_cols = temp.drop(columns=['SNo']).select_dtypes(include=['float64','int64']).columns.tolist()

#     # Define transformer
#     transformer = ColumnTransformer(
#         transformers=[
#             ('scale', StandardScaler(), float_cols)
#         ],
#         remainder='passthrough'  # Leave other columns untouched
#     )

#     # Fit and transform
#     transformed = transformer.fit_transform(temp)

#     # Convert back to DataFrame with updated column names
#     new_columns = float_cols + [col for col in temp.columns if col not in float_cols]
#     df_transformed = pd.DataFrame(transformed, columns=new_columns)

#     df_transformed=df_transformed[df_transformed.columns[::-1]]
    
#     nbrs = NearestNeighbors(n_neighbors=11,metric='manhattan').fit(df_transformed.drop(columns=['SNo','name','team','league','positions'])[['gls','ast']])

# # Find neighbors to the query_point
#     distances, indices = nbrs.kneighbors(df_transformed[df_transformed['SNo']==1].drop(columns=['SNo','name','positions','team','league'])[['gls','ast']])

    # # Show results
    # display("Query point:", required)
    # print("Nearest neighbors (indices):", indices[0][1:])
    # display("Nearest neighbors (points):", temp.iloc[indices[0][1:]])
    # print("Distances:", distances[0])