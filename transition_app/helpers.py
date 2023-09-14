import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import minmax_scale

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

# def load_tracking_data(folder, selections):
#     tracking_data = []
#     gameIds = []
    
#     game_list = os.listdir(folder)
    
#     dict = {'0042100301': 'Miami vs Boston Game 1', '0042100302': 'Miami vs Boston Game 2','0042100303': 'Miami vs Boston Game 3', 
#             '0042100304': 'Miami vs Boston Game 4', '0042100305': 'Miami vs Boston Game 5', '0042100306': 'Miami vs Boston Game 6',
#             '0042100307': 'Miami vs Boston Game 7', '0042100311': 'Golden State vs Dallas Game 1', '0042100312': 'Golden State vs Dallas Game 2',
#             '0042100313': 'Golden State vs Dallas Game 3', '0042100314': 'Golden State vs Dallas Game 4', '0042100315': 'Golden State vs Dallas Game 5',
#             '0042100401': 'Golden State vs Boston Game 1', '0042100402': 'Golden State vs Boston Game 2', '0042100403': 'Golden State vs Boston Game 3', 
#             '0042100404': 'Golden State vs Boston Game 4', '0042100405': 'Golden State vs Boston Game 5', '0042100406': 'Golden State vs Boston Game 6'}
#     gameNames_dict = {v: k for k, v in dict.items()}
    
#     if selections['Game'] != 'All':
#         gameId = gameNames_dict[selections['Game']]
#         game_list = [x for x in game_list if gameId in x]
#     if selections['Team'] != 'All':
#         game_list = [x for x in game_list if selections['Team'] in x]
#     series = selections['Series']
#     if series != 'All':
#         if series == 'ECF':
#             series_code = '30'
#         elif series == 'WCF':
#             series_code = '31'
#         else:
#             series_code = '40'
#         game_list = [x for x in game_list if series_code in x]
            
#     for file in os.listdir(folder):
#         if file in game_list:
#             data = pd.read_pickle(folder+file)
#             gameId = file[0:10]
            
#             tracking_data.append(data)
#             gameIds.append(gameId)

#     df = pd.DataFrame(list(zip(tracking_data, gameIds)), columns =['Name', 'val'])
#     return df
    
        

def add_selectbox(df, columnName, label, sidebar=True, key=None):
    # Add a selectbox to the sidebar:
    options = np.append(['All'], sorted(df[columnName].unique()))
    if sidebar:
        selection = st.sidebar.selectbox(label, options, index=0)
    else:
        selection = st.selectbox(label, options, index=0, key=key)
    return selection

def update_df(df, selection, columnName, colType):
    #display dataframe based on selectbox selection

    if selection == 'All':
        data = df
    else:
        if colType == 'string':
            data = df[df[columnName] == selection]
        else:
            data = df[df[columnName] == int(selection)]
    return data


def create_selectbox(df, col, label, sidebar=True, key=None, col_type='string'):
    selection = add_selectbox(df, col, label, sidebar, key=key)
    data = update_df(df, selection, col, col_type)
    return selection, data

def get_num_games(df, var_name):
    '''
    var_name is either: 'Team Name', 'Driver', 'Passer'
    '''
    games_by_team = df.groupby([var_name])['Game Id'].unique()
    num_games = {}
    for team in games_by_team.index:
        num_games[team] = len(games_by_team[team])
        
    return num_games

# def get_num_games_player(df, col):
#     games_by_team = df.groupby([col])['Game Id'].unique()
#     num_games = {}
#     for team in games_by_team.index:
#         num_games[team] = len(games_by_team[team])
        
#     return num_games


def add_num_games(df, num_games):
    num_games_df = pd.DataFrame.from_dict(num_games, orient='index', columns=['Number of Games Played'])
    num_games_df['Team'] = num_games_df.index
    num_games_df.reset_index(drop=True, inplace=True)    
    
    df = df.merge(num_games_df, left_on=['Team Name'], right_on=['Team'], how='left')
    df.drop(['Team'], axis=1, inplace=True)
    
    return df

def get_value(x):
    return x.iloc[0]

def get_ppp(df):
    #assume each free throw opportunity ended in 1.5 points (75% free throw average estimate)
    made_shots = df[df['OutcomeMSG'] == 1]
    made_shots_unique = made_shots.groupby(['Transition Index']).agg({'OutcomeMSGaction': get_value})

    points3 = len(made_shots_unique[made_shots_unique['OutcomeMSGaction'].isin([1,79])])*3 
    points2 = len(made_shots_unique[~made_shots_unique['OutcomeMSGaction'].isin([1,79])])*2
    freethrows = len(df[df['OutcomeMSG']==6])*1.5
    num_possessions = len(np.unique(df['Transition Index'].values))

    try:
        ppp = round((points3 + points2 + freethrows) / num_possessions, 2) #len(df),2)
    except ZeroDivisionError:
        ppp = 0
    
    return ppp

def get_ppp_df(df, min_val, max_val, col, linechart=True, values=None):
    ppp_dict = {}
    for team in np.unique(df['Team Name'].values):
        team_df = df[df['Team Name'] == team]
        ppp_dict[team] = []
        if linechart:
            for def_passed in range(min_val,max_val):
                if col == '# Defenders Passed':
                    curr_data = team_df[team_df[col] == def_passed]
                else:
                    curr_data = team_df[team_df[col] >= def_passed]
                ppp_dict[team].append(get_ppp(curr_data))
        else:
            for var in values:
                curr_data = team_df[team_df[col] == var]
                ppp_dict[team].append(get_ppp(curr_data))
    return pd.DataFrame.from_dict(ppp_dict)

def get_ppp_player_df(df, group_by_col):
    players = []
    ppp_list = []
    team_list = []
    for player in np.unique(df[group_by_col].values):
        group_df = df[df[group_by_col] == player]
        players.append(player)
        ppp_list.append(get_ppp(group_df))
        team_list.append(group_df.iloc[0]['Team Name'])
        #ppp_dict[player] = [get_ppp(group_df)]
    return pd.DataFrame({'Player': players, 'Points per Possession': ppp_list, 'Team': team_list})

def get_ppp_team_df(df):
    teams = []
    ppp_list = []
    for team in np.unique(df['Team Name'].values):
        group_df = df[df['Team Name'] == team]
        teams.append(team)
        ppp_list.append(get_ppp(group_df))
    return pd.DataFrame({'Team Name': teams, 'Points per Possession': ppp_list})

#for placing text in multiple positions on scatter plot to reduce overlap
def improve_text_position(x):
    """ it is more efficient if the x values are sorted """
    # fix indentation 
    positions = ['bottom center', 'top center']  # you can add more: left center ...
    return [positions[i % len(positions)] for i in range(len(x))]


def scale_range(data, min_val, max_val):
    return minmax_scale(data, (min_val, max_val))

def get_paint_touches(data, paint):
        #count number of drives that get into paint (end in paint)
    drive_end_locs = data['Drive End'].values
    outcomes = data['OutcomeMSG'].values
    trans_ind = data['Transition Index'].values
    outcome_action = data['OutcomeMSGaction'].values
    distance = data['Drive Distance'].values
    ball_locs_x = [x[0] for x in drive_end_locs]
    ball_locs_y = [x[1] for x in drive_end_locs]
    temp_df = pd.DataFrame(list(zip(ball_locs_x, ball_locs_y, outcomes, outcome_action, distance, trans_ind)), columns=['X', 'Y', 'OutcomeMSG', 'OutcomeMSGaction', 'Drive Distance', 'Transition Index'])
    if paint:
        temp_df = temp_df[(temp_df['X'] > 28) & (temp_df['X'] < 45)]
        temp_df = temp_df[(temp_df['Y'] > -8) & (temp_df['Y'] < 8)]
    else:
        temp_df = temp_df[(temp_df['X'] < 28)]
        #temp_df = temp_df[(temp_df['Y'] > -8) & (temp_df['Y'] < 8)]
        
    num_paint_touches = len(temp_df)

    #count number of times the team gets a shot when the paint is reached
    shots_paint_touches = temp_df[temp_df['OutcomeMSG'].isin([1,2,6])]
    num_shots = len(np.unique(shots_paint_touches['Transition Index'].values))
    

    return num_paint_touches, num_shots, temp_df