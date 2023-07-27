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

def add_selectbox(df, columnName, label):
    # Add a selectbox to the sidebar:
    options = np.append(['All'], sorted(df[columnName].unique()))
    selection = st.sidebar.selectbox(label, options, index=0)
    return selection

def update_df(df, selection, columnName):
    #display dataframe based on selectbox selection
    if selection == 'All':
        data = df
    else:
        data = df[df[columnName] == selection]
    
    return data

def create_selectbox(df, col, label):
    selection = add_selectbox(df, col, label)
    data = update_df(df, selection, col)
    return selection, data

def get_num_games(df):
    games_by_team = df.groupby(['Team Name'])['Game Id'].unique()
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