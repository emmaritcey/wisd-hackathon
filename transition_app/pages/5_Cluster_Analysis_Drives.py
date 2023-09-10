import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import sys
from sklearn.cluster import KMeans
 
# adding Folder_2/subfolder to the system path
sys.path.append('/Users/emmaritcey/Documents/basketball_research/wisd-hackathon')
from src.visualization.draw_court import make_fig
from helpers import load_data, create_selectbox, get_num_games, get_ppp, get_ppp_df, get_ppp_player_df, get_ppp_team_df
st.set_page_config(layout="wide")


def cluster_data(data):
    drive_start_x = [x[0] for x in data['Drive Start']]
    drive_start_y = [x[1] for x in data['Drive Start']]

    drive_end_x = [x[0] for x in data['Drive End']]
    drive_end_y = [x[1] for x in data['Drive End']]

    drive_dict = {'Drive Start X': drive_start_x, 'Drive Start Y': drive_start_y, 'Drive End X': drive_end_x, 'Drive End Y': drive_end_y}
    df = pd.DataFrame(drive_dict)
    
    kmeans = KMeans(n_clusters=8, init='random', n_init='auto', random_state=1)
    kmeans.fit(df)
    y_kmeans = kmeans.predict(df)
    
    return y_kmeans

def create_sidebar(df):

    #Selection Boxes
    series_selection, data = create_selectbox(df, 'Series', 'Series:')
    game_selection, data = create_selectbox(data, 'Game Title', 'Game:')
    team_selection, data = create_selectbox(data, 'Team Name', 'Team:')
    driver_selection, data = create_selectbox(data, 'Driver', 'Drives Made By:')
    trigger_selection, data = create_selectbox(data, 'Transition Trigger', 'Transition Initiated By:')
    outcome_selection, data = create_selectbox(data, 'Outcome', 'Transition Outcome:')

    selections = {'Series': series_selection, 'Game': game_selection, 'Team': team_selection, 'Driver': driver_selection,
                'Trigger': trigger_selection, 'Outcome': outcome_selection}

    #Check boxes
    #show_raw_data = st.sidebar.checkbox('Show Raw Data')

    return data, selections


def display1(data, possessions_df, selections):
    color_dict = {0: 'b', 1: 'r', 2: 'g', 3: 'm', 4: 'y', 5: 'c', 6: 'w', 7: 'tab:orange'}
    clusters = data['Drive Clusters'].values

    colors = [color_dict[i] for i in clusters]

    #subplots = st.checkbox('Click to Show Each Cluster on Separate Court')
    center_coord_x = 0
    center_coord_y = 0
    # if subplots == False:
    #     plt.style.use('dark_background')
    #     fig = plt.figure(figsize=(12, 7))

    #     ax = make_fig(cc_x=center_coord_x, cc_y=center_coord_y)
    #     plt.xlim(center_coord_x-50, center_coord_x+50)
    #     plt.ylim(center_coord_y-30, center_coord_y+30)
    #     for idx in data.index.values:
    #         #if y_kmeans[idx]==0:
    #             #try:
    #         x = data['Drive Start'].loc[idx][0]
    #         y = data['Drive Start'].loc[idx][1]
    #         dx = data['Drive End'].loc[idx][0] - x
    #         dy = data['Drive End'].loc[idx][1] - y
    #         c = color_dict[data['Drive Clusters'].loc[idx]]
    #         plt.arrow(x,y,dx,dy, head_width=0.8, color=c)
        
    #     ax.set_xticks([])
    #     ax.set_yticks([])
    #     st.pyplot(fig)  
    # else:
    titles = ['Front Court, Right Drives', 'Front Court, Left Drives', '3/4 Court, Right Drives', '3/4 Court Left Drives',
                'Back Court, Right Drives', 'Back Court, Left Drives', 'Full Court Drives', 'Back Court, Short Drives']
    plt.style.use('dark_background')
    n_rows = 4
    n_cols = 2
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(12, 16))
    
    total_num_drives = len(data)
    perc_drives_dict = {}
    ppp_dict = {}
    cluster_num = 0
    for row in range(0,n_rows):
        for col in range(0,n_cols):
            curr_data = data[data['Drive Clusters']==cluster_num]
            perc_drives = round(len(curr_data)/total_num_drives*100,2)
            perc_drives_dict[titles[cluster_num]] = perc_drives
            ppp = get_ppp(curr_data)
            ppp_dict[titles[cluster_num]] = ppp
            axs[row, col] = make_fig(axs[row,col], cc_x=center_coord_x, cc_y=center_coord_y)
            for idx in data.index.values:
                if data['Drive Clusters'].loc[idx]==cluster_num:
                    #try:
                    x = data['Drive Start'].loc[idx][0]
                    y = data['Drive Start'].loc[idx][1]
                    dx = data['Drive End'].loc[idx][0] - x
                    dy = data['Drive End'].loc[idx][1] - y
                    c = color_dict[data['Drive Clusters'].loc[idx]]
                    axs[row,col].arrow(x,y,dx,dy, head_width=0.8, color=c)
                axs[row,col].set_xticks([])
                axs[row,col].set_yticks([])
            axs[row,col].set_title(titles[cluster_num] + ' -> ' + str(perc_drives) + '%')
            cluster_num += 1
    st.pyplot(fig)
        
    st.header('Compare All Teams and All Players in Each Cluster')
    cluster_selection, data_filtered = create_selectbox(data, 'Drive Cluster Name', 'Select a Drive Cluster:', False)
    
    total_counts = data.groupby(['Team Name'])['Drive Clusters'].count()
    total_counts_player = data.groupby(['Driver'])['Drive Clusters'].count()
    
    st.subheader('Team Breakdowns')
    st.markdown('Note: To include all teams, make sure "All" is selected on the sidebar under "Teams"')
    if selections['Team'] == 'All':
        if cluster_selection != 'All': #COMPARING THE DRIVES BY TEAM, SELECT SPECIFIC CLUSTER


            cluster_counts_team = data_filtered.groupby(['Team Name'])['Drive Clusters'].count()
            perc_drives_team =  round(cluster_counts_team / total_counts * 100,2)

            col1, col2 = st.columns(2)
            with col1: 
                fig2 = px.bar(x = perc_drives_team.index, y = perc_drives_team) #color_discrete_sequence=['green', 'blue', 'gold', 'red']
                fig2.update_layout(width=550, 
                                height=400,  
                                title='Percentage of Drives in Selected Drive Cluster By Team', 
                                title_x=0.2,
                                xaxis_title="Drive Cluster",
                                yaxis_title=None) 
                st.plotly_chart(fig2)
                
            with col2:
                ppp_team = get_ppp_team_df(data_filtered)
                
                fig3 = px.bar(x = ppp_team['Team Name'], y = ppp_team['Points per Possession'])
                fig3.update_layout(width=550, 
                                height=400,  
                                title='Team PPP For Selected Drive Cluster', 
                                title_x=0.3,
                                xaxis_title="Drive Cluster",
                                yaxis_title=None) 
                st.plotly_chart(fig3)
                
            
    st.subheader('Player Breakdowns')
    st.markdown('Note: To include all players, make sure "All" is selected on the sidebar under "Drives Made By"')
    if selections['Driver'] == 'All':
        if cluster_selection != 'All': 
            cluster_counts_player = data_filtered.groupby(['Driver'])['Drive Clusters'].count()
            perc_drives_player =  round(cluster_counts_player / total_counts_player * 100,2)
            
            fig2 = px.bar(x = perc_drives_player.index, y = perc_drives_player) #color_discrete_sequence=['green', 'blue', 'gold', 'red']
            fig2.update_layout(width=1100, 
                            height=500,  
                            title='Percentage of Drives in Selected Drive Cluster By Player', 
                            title_x=0.2,
                            xaxis_title="Drive Cluster",
                            yaxis_title=None) 
            st.plotly_chart(fig2)
            
            ppp_player = get_ppp_player_df(data_filtered, 'Driver')
            
            fig3 = px.bar(x = ppp_player['Player'], y = ppp_player['Points per Possession'])
            fig3.update_layout(width=1100, 
                            height=500,  
                            title='Team PPP For Selected Drive Cluster of Individual Players', 
                            title_x=0.3,
                            xaxis_title="Drive Cluster",
                            yaxis_title=None) 
            st.plotly_chart(fig3)
            
    st.header('Assess an Individual Team or an Individual Player')
    
    st.subheader('Team Breakdown')
    st.markdown('Note: Must select a team from "Team" in the sidebar')
    if selections['Team'] != 'All':
        col1, col2 = st.columns(2)
        with col1: 
            sorted_perc_drives = sorted(perc_drives_dict.items(), key=lambda x:x[1], reverse=True)
            sorted_perc_drives_dict = dict(sorted_perc_drives)
            fig2 = px.bar(x = sorted_perc_drives_dict.keys(), y = sorted_perc_drives_dict.values())
            fig2.update_layout(width=600, 
                            height=400,  
                            title='Percentage of Drives in Each Drive Cluster', 
                            title_x=0.4,
                            xaxis_title="Drive Cluster") 
            st.plotly_chart(fig2)
        
        with col2:
            sorted_ppp = sorted(ppp_dict.items(), key=lambda x:x[1], reverse=True)
            sorted_ppp_dict = dict(sorted_ppp)
            fig3 = px.bar(x = sorted_ppp_dict.keys(), y = sorted_ppp_dict.values())
            fig3.update_layout(width=600, 
                            height=400,  
                            title='Team PPP For Each Drive Cluster', 
                            title_x=0.4,
                            xaxis_title="Drive Cluster") 
            st.plotly_chart(fig3)
            
        
    st.subheader('Player Breakdown')
    st.markdown('Note: Must select a Player from "Drives Made By" in the sidebar')
    if selections['Driver'] != 'All':
        num_games_dict = get_num_games(data, 'Driver')
        players = np.array(list(num_games_dict.keys())) #get list of players
        num_games = list(num_games_dict.values())
        #minimum number of games played:
        if max(num_games) > 1:
            min_num_games = st.slider('Minimum Number of Games Played', min_value=1, max_value=max(num_games))
            min_games_indices = np.where(np.array(num_games)>=min_num_games) #get indices of players who played in min_num_games
            eligible_players = players[min_games_indices] #get player names of those who played in min_num_games
            data = data[data['Passer'].isin(eligible_players)] #keep the data only for the players who played in min_num_games

                
        col1, col2 = st.columns(2)
        with col1: 
            sorted_perc_drives = sorted(perc_drives_dict.items(), key=lambda x:x[1], reverse=True)
            sorted_perc_drives_dict = dict(sorted_perc_drives)
            fig2 = px.bar(x = sorted_perc_drives_dict.keys(), y = sorted_perc_drives_dict.values())
            fig2.update_layout(width=600, 
                            height=400,  
                            title='Percentage of Drives in Each Drive Cluster', 
                            title_x=0.4,
                            xaxis_title="Drive Cluster") 
            st.plotly_chart(fig2)
        
        with col2:
            sorted_ppp = sorted(ppp_dict.items(), key=lambda x:x[1], reverse=True)
            sorted_ppp_dict = dict(sorted_ppp)
            fig3 = px.bar(x = sorted_ppp_dict.keys(), y = sorted_ppp_dict.values())
            fig3.update_layout(width=600, 
                            height=400,  
                            title='Team PPP For Each Drive Cluster', 
                            title_x=0.4,
                            xaxis_title="Drive Cluster") 
            st.plotly_chart(fig3)
        
        
def main():
    
    st.title('NBA Transition Tendencies: Driving')

    drive_df = load_data('data/transition/drive_stats.pkl')
    possessions_df = load_data('data/transition/possession_summaries.pkl')

    drive_df.loc[np.isnan(drive_df['# Defenders Passed']), '# Defenders Passed'] = np.nan
    drive_df['Speed'] = round(drive_df['Total Drive Distance']/drive_df['Drive Length (sec)'], 2)
    drive_df.loc[drive_df['Transition Trigger'] == 'SHOT', 'Transition Trigger'] = "Made Shot"
    drive_df.loc[drive_df['Transition Trigger'] == 'REB', 'Transition Trigger'] = "Defensive Rebound"
    drive_df.loc[drive_df['Transition Trigger'] == 'TO', 'Transition Trigger'] = "Turnover"
    drive_df.loc[drive_df['Outcome'] == 'foul', 'Outcome'] = "non-shooting foul"
    
    drive_clusters_init = cluster_data(drive_df)
    
    cluster_dict = {0: 6, 1: 7, 2: 1, 3: 5, 4: 3, 5: 4, 6: 2, 7: 0}
    drive_clusters = [cluster_dict[i] for i in drive_clusters_init]
    
    cluster_names_dict =  {0:'Front Court, Right Drives', 1:'Front Court, Left Drives', 2:'3/4 Court, Right Drives', 
                           3:'3/4 Court Left Drives', 4:'Back Court, Right Drives', 5:'Back Court, Left Drives', 
                           6:'Full Court Drives', 7:'Back Court, Short Drives'}
    cluster_names = [cluster_names_dict[i] for i in drive_clusters]
    
    drive_df['Drive Clusters'] = drive_clusters
    drive_df['Drive Cluster Name'] = cluster_names

    drive_data, selections = create_sidebar(drive_df) 

    
    drive_data_selected_team = display1(drive_data, possessions_df, selections)
    
    
main()