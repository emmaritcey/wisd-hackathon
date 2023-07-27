import streamlit as st
import pandas as pd
import numpy as np

#update this/advance it later if needed
@st.cache_data
def load_data(file):
    #LOAD THE PASS DATA
    # Create a text element and let the reader know the data is loading.
    data_load_state = st.text('Loading data...')
    df = pd.read_pickle(file)
    data_load_state.text('Loading data...done!')
    data_load_state.text('')
    return df

def add_selectbox(df, columnName, label, sidebar=True):
    # Add a selectbox to the sidebar:
    options = np.append(['All'], sorted(df[columnName].unique()))
    if sidebar:
        selection = st.sidebar.selectbox(label, options, index=0)
    else:
        selection = st.selectbox(label, options, index=0)
    return selection

def update_df(df, selection, columnName):
    #display dataframe based on selectbox selection
    if selection == 'All':
        data = df
    else:
        data = df[df[columnName] == selection]
    
    return data

def create_selectbox(df, col, label, sidebar=True):
    selection = add_selectbox(df, col, label, sidebar)
    data = update_df(df, selection, col)
    return selection, data

def get_num_games(df):
    games_by_team = df.groupby(['Team Name'])['Game Id'].unique()
    num_games = {}
    for team in games_by_team.index:
        num_games[team] = len(games_by_team[team])
        
    return num_games

def get_num_games_player(df, col):
    games_by_team = df.groupby([col])['Game Id'].unique()
    num_games = {}
    for team in games_by_team.index:
        num_games[team] = len(games_by_team[team])
        
    return num_games


def add_num_games(df, num_games):
    num_games_df = pd.DataFrame.from_dict(num_games, orient='index', columns=['Number of Games Played'])
    num_games_df['Team'] = num_games_df.index
    num_games_df.reset_index(drop=True, inplace=True)    
    
    df = df.merge(num_games_df, left_on=['Team Name'], right_on=['Team'], how='left')
    df.drop(['Team'], axis=1, inplace=True)
    
    return df


def get_ppp(df):
    #assume each free throw opportunity ended in 1.5 points (75% free throw average estimate)
    made_shots = df[df['OutcomeMSG'] == 1]
    points3 = len(made_shots[made_shots['OutcomeMSGaction'].isin([1,79])])*3 
    points2 = len(made_shots[~made_shots['OutcomeMSGaction'].isin([1,79])])*2
    freethrows = len(df[df['OutcomeMSG']==6])*1.5
    try:
        ppp = round((points3 + points2 + freethrows) / len(df),2)
    except ZeroDivisionError:
        ppp = np.nan
    
    return ppp

def get_ppp_df(df, min_val, max_val, col):
    ppp_dict = {}
    for team in np.unique(df['Team Name'].values):
        team_df = df[df['Team Name'] == team]
        ppp_dict[team] = []
        for def_passed in range(min_val,max_val):
            curr_data = team_df[team_df[col] >= def_passed]
            ppp_dict[team].append(get_ppp(curr_data))
    return pd.DataFrame.from_dict(ppp_dict)

