import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import sys
 
# adding Folder_2/subfolder to the system path
sys.path.append('/Users/emmaritcey/Documents/basketball_research/wisd-hackathon')
from src.visualization.draw_court import make_fig
from helpers import load_data, create_selectbox, get_num_games, get_ppp, get_ppp_df, get_num_games_player, get_ppp_player_df, improve_text_position
st.set_page_config(layout="wide")


def create_sidebar(df):

    #Selection Boxes
    series_selection, data = create_selectbox(df, 'Series', 'Series:')
    team_selection, data = create_selectbox(data, 'Team Name', 'Team:')
    outcome_selection, data = create_selectbox(data, 'Outcome', 'Transition Outcome:')
    
    #selections = {'Series': series_selection, 'Team':, team_selection}
    return data

def display1(data):

    
    st.header('Team Breakdowns')
    
    num_games = get_num_games(data, 'Team Name')
    #manually find number of wins and losses and divide to find mean for each
    num_wins_losses = data.groupby(['NBA Game Id', 'Team Name']).agg({'Win': 'first'})
    num_wins = num_wins_losses.groupby(['Team Name']).agg({'Win': 'sum'})
    num_losses = np.array(list(num_games.values())) - num_wins['Win'].values
    
    num_wins['Loss'] = num_losses
    num_wins_losses = num_wins
    num_wins_losses.columns = ['Wins', 'Losses']
    
    data['Win'] = data['Win'].map({False: 'Losses', True: 'Wins',})

    num_drives = data.groupby(by=['Team Name', 'Win'], as_index=False).agg({'# Defenders Passed': "count"})
    num_drives.columns = ['Team Name', 'Win', '# of Drives']
    
    num_drives = pd.DataFrame(num_drives)
    num_wins_losses_list = []
    for ind in num_wins_losses.index:
        num_wins_losses_list.append(num_wins_losses.loc[ind]['Losses'])
        num_wins_losses_list.append(num_wins_losses.loc[ind]['Wins'])
    num_drives['Num Games'] = num_wins_losses_list
    mean_drives = num_drives['# of Drives'].values / num_drives['Num Games'].values

    fig4 = px.bar(x=num_drives['Team Name'],
                y=mean_drives,
                color=num_drives["Win"],
                barmode="group")
    fig4.update_layout(legend_title=None)
    st.plotly_chart(fig4)

       
    #MEAN NUMBER OF DEFENDERS PASSED PER DRIVE 
    def_passed_means = data.groupby(by=['Team Name', 'Win'], as_index=False).agg({'# Defenders Passed': "mean"})
    fig = px.bar(data_frame=def_passed_means,
                 x="Team Name",
                 y="# Defenders Passed",
                 color="Win",
                 barmode="group")
    fig.update_layout(legend_title=None)
    st.plotly_chart(fig)
    
    #NUMBER OF PAINT TOUCHES/PERCENT OF DRIVES ENDING IN PAINT TOUCH
    num_painttouches_team = data.groupby(['Team Name', 'Win'], as_index=False).agg({'Paint Touch': 'sum'})
    perc_painttouches_team = data.groupby(['Team Name', 'Win'], as_index=False).agg({'Paint Touch': 'mean'}) #percent of drives that end with a paint touch
    
    # #manually find number of wins and losses and divide to find mean for each
    # num_painttouches_team = pd.DataFrame(num_painttouches_team)
    # num_wins_losses_list = []
    # for ind in num_wins_losses.index:
    #     num_wins_losses_list.append(num_wins_losses.loc[ind]['Losses'])
    #     num_wins_losses_list.append(num_wins_losses.loc[ind]['Wins'])
    # num_painttouches_team['Num Games'] = num_wins_losses_list
    # mean_painttouches_team = num_painttouches_team['Paint Touch'].values / num_painttouches_team['Num Games'].values
     
    # fig2 = px.bar(x=num_painttouches_team['Team Name'],
    #               y=mean_painttouches_team,
    #               color=num_painttouches_team['Win'],
    #               barmode="group")
    # st.plotly_chart(fig2)
    
    fig3 = px.bar(data_frame=perc_painttouches_team,
                 x="Team Name",
                 y="Paint Touch",
                 color="Win",
                 barmode="group")
    fig3.update_layout(legend_title=None)
    st.plotly_chart(fig3)

    
def display2(data):
    '''
    PLAYER BREAKDOWNS
    '''
    
    num_games = get_num_games(data, 'Driver')
    players = np.array(list(num_games.keys())) #get list of players
    
    #manually find number of wins and losses and divide to find mean for each
    num_wins_losses = data.groupby(['NBA Game Id', 'Driver']).agg({'Win': 'first'})
    num_wins = num_wins_losses.groupby(['Driver']).agg({'Win': 'sum'})
    num_losses = np.array(list(num_games.values())) - num_wins['Win'].values
    
    num_wins['Loss'] = num_losses
    num_wins_losses = num_wins
    num_wins_losses.columns = ['Wins', 'Losses']
    
    #data['Win'] = data['Win'].map({False: 'Losses', True: 'Wins',})
    #num_drives = data.groupby(by=['Driver', 'Win'], as_index=False).agg({'# Defenders Passed': "count"})
    num_drives = data.groupby(by=['Driver', 'Win'])['# Defenders Passed'].count().unstack(fill_value=0).stack().reset_index()

    num_drives.columns = ['Driver', 'Win', '# of Drives']
    
    #Sliders
    #minimum number of drives per game:
    num_drives_total = data.groupby(by=['Driver'])['# Defenders Passed'].count()
    num_drives_total = pd.DataFrame(num_drives_total)
    num_drives_total.columns = ['# of Drives']
 
    num_drives_per_game = [round(num_drives_total.loc[x][0]/num_games[x],2) for x in num_drives_total.index]
    num_drives_per_game_df = pd.DataFrame({'Player':num_drives_total.index, '# of Drives': num_drives_per_game})
    min_num_drives = st.slider('Minimum Number of Transition Drives Per Game for a Single Player', min_value=0, max_value=int(max(np.round(num_drives_per_game_df['# of Drives'].values))))
    num_drives_total = num_drives_total[num_drives_total['# of Drives'] >= min_num_drives]
    data = data[data['Driver'].isin(num_drives_total.index)]

    #minimum number of games played:
    num_games_list = list(num_games.values())
    if max(num_games_list) > 1:
        min_num_games = st.slider('Minimum Number of Games Played', min_value=1, max_value=max(num_games_list))
        min_games_indices = np.where(np.array(num_games_list)>=min_num_games) #get indices of players who played in min_num_games
        eligible_players = players[min_games_indices] #get player names of those who played in min_num_games
        data = data[data['Driver'].isin(eligible_players)] #keep the data only for the players who played in min_num_games
    filtered_num_games = get_num_games(data,'Driver')
    
    #manually find number of wins and losses and divide to find mean for each
    num_wins_losses = data.groupby(['NBA Game Id', 'Driver']).agg({'Win': 'first'})
    num_wins = num_wins_losses.groupby(['Driver']).agg({'Win': 'sum'})
    num_losses = np.array(list(filtered_num_games.values())) - num_wins['Win'].values
    
    num_wins['Loss'] = num_losses
    num_wins_losses = num_wins
    num_wins_losses.columns = ['Wins', 'Losses']
    
    data['Win'] = data['Win'].map({False: 'Losses', True: 'Wins',})
    #num_drives = data.groupby(by=['Driver', 'Win'], as_index=False).agg({'# Defenders Passed': "count"})
    num_drives = data.groupby(by=['Driver', 'Win'])['# Defenders Passed'].count().unstack(fill_value=0).stack().reset_index()

    num_drives.columns = ['Driver', 'Win', '# of Drives']

    
    #num_drives
    #num_drives = pd.DataFrame(num_drives)
    num_wins_losses_list = []

    for ind in num_wins_losses.index:
        num_wins_losses_list.append(num_wins_losses.loc[ind]['Losses'])
        num_wins_losses_list.append(num_wins_losses.loc[ind]['Wins'])

    num_drives['Num Games'] = num_wins_losses_list
    mean_drives = num_drives['# of Drives'].values / num_drives['Num Games'].values
    
    #MEAN NUMBER OF DRIVES PER GAME
    fig4 = px.bar(x=num_drives['Driver'],
                y=mean_drives,
                color=num_drives["Win"],
                barmode="group")
    fig4.update_layout(legend_title=None,
                       width = 1200)
    st.plotly_chart(fig4)
    
    #MEAN NUMBER OF DEFENDERS PASSED PER DRIVE 
    def_passed_means = data.groupby(by=['Driver', 'Win'], as_index=False).agg({'# Defenders Passed': "mean"})
    fig = px.bar(data_frame=def_passed_means,
                 x="Driver",
                 y="# Defenders Passed",
                 color="Win",
                 barmode="group")
    fig.update_layout(legend_title=None,
                      width = 1200)
    st.plotly_chart(fig)
    
    #NUMBER OF PAINT TOUCHES/PERCENT OF DRIVES ENDING IN PAINT TOUCH
    num_painttouches_team = data.groupby(['Driver', 'Win'], as_index=False).agg({'Paint Touch': 'sum'})
    perc_painttouches_team = data.groupby(['Driver', 'Win'], as_index=False).agg({'Paint Touch': 'mean'}) #percent of drives that end with a paint touch
    
    fig3 = px.bar(data_frame=perc_painttouches_team,
                 x="Driver",
                 y="Paint Touch",
                 color="Win",
                 barmode="group")
    fig3.update_layout(legend_title=None,
                       width = 1200)
    st.plotly_chart(fig3)
    
    
#def display3(data):

    

def main():
    st.title('NBA Transition Tendencies: Wins vs Losses')

    pass_df = load_data('data/transition/pass_stats.pkl')
    drive_df = load_data('data/transition/drive_stats.pkl')
    possessions_df = load_data('data/transition/possession_summaries.pkl')
    
    drive_df = drive_df[drive_df['# Defenders Passed'].notna()]
    #drive_df.loc[np.isnan(drive_df['# Defenders Passed']), '# Defenders Passed'] = np.nan
    drive_df['Speed'] = round(drive_df['Total Drive Distance']/drive_df['Drive Length (sec)'], 2)
    drive_df.loc[drive_df['Transition Trigger'] == 'SHOT', 'Transition Trigger'] = "Made Shot"
    drive_df.loc[drive_df['Transition Trigger'] == 'REB', 'Transition Trigger'] = "Defensive Rebound"
    drive_df.loc[drive_df['Transition Trigger'] == 'TO', 'Transition Trigger'] = "Turnover"
    drive_df.loc[drive_df['Outcome'] == 'foul', 'Outcome'] = "non-shooting foul"
    
    pass_df = pass_df[pass_df['# Defenders Passed'].notna()]
    #pass_df.loc[np.isnan(pass_df['# Defenders Passed']), '# Defenders Passed'] = None
    pass_df['Pass Distance'] = round(pass_df['Pass Distance'] * 2) / 2
    pass_df.loc[pass_df['Transition Trigger'] == 'SHOT', 'Transition Trigger'] = "Made Shot"
    pass_df.loc[pass_df['Transition Trigger'] == 'REB', 'Transition Trigger'] = "Defensive Rebound"
    pass_df.loc[pass_df['Transition Trigger'] == 'TO', 'Transition Trigger'] = "Turnover"
    pass_df.loc[pass_df['Outcome'] == 'foul', 'Outcome'] = "non-shooting foul"
    
    
    drive_df = create_sidebar(drive_df)
    #display1(drive_df, drive_win_df, drive_loss_df)
    
    display3(drive_df)
    

main()