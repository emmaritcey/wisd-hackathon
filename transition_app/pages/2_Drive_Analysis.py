import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import sys
 
# adding Folder_2/subfolder to the system path
sys.path.append('/Users/emmaritcey/Documents/basketball_research/wisd-hackathon')
from src.visualization.draw_court import make_fig
from helpers import load_data, create_selectbox, get_num_games, get_ppp, get_ppp_df, get_ppp_player_df, get_num_games_player, improve_text_position
st.set_page_config(layout="wide")



def create_sidebar(df):

    #Selection Boxes
    series_selection, data = create_selectbox(df, 'Series', 'Series:')
    game_selection, data = create_selectbox(data, 'Game Title', 'Game:')
    driver_selection, data = create_selectbox(data, 'Driver', 'Drives Made By:')
    trigger_selection, data = create_selectbox(data, 'Transition Trigger', 'Transition Initiated By:')
    outcome_selection, data = create_selectbox(data, 'Outcome', 'Transition Outcome:')

    selections = {'Series': series_selection, 'Game': game_selection, 'Driver': driver_selection,
                'Trigger': trigger_selection, 'Outcome': outcome_selection}

    #Check boxes
    show_raw_data = st.sidebar.checkbox('Show Raw Data')

    return show_raw_data, data, selections


def display1(data, possessions_df, selections):
    '''
    Court and drives figure with extra widgets
    '''
    st.header('Overview of Drives')
    st.markdown('- Drives that belong to possessions that ended in a :red[**MADE SHOT**] within the first 8 seconds of the shot clock are represented by :red[**RED**] arrows')
    st.markdown('- Drives that belong to possessions that ended in a :blue[**MISSED SHOT**] within the first 8 seconds of the shot clock are represented by :blue[**BLUE**] arrows')
    st.markdown('- Drives that belong to possessions that ended in **NO SHOT** within the first 8 seconds of the shot clock are represented by **WHITE** arrows')
    st.markdown("- Note that the arrows only depict the start and end location of a drive. Players actual track between these two locations would be much more variable.")
    col1, col2 = st.columns([1,3])
    
    with col1: #WIDGETS/FILTERS
        
        
        st.markdown('##### Displaying Drives for:')
        _, data = create_selectbox(data, 'Team Name', 'Team:', False)
            
        col1_2, col2_2 = st.columns(2)
        with col1_2:
            #Number Increments
            # # of drives in a possession
            options = np.append(['At least 1'], sorted(possessions_df['# Drives'].unique())[1:])
            num_drives = st.selectbox('Number of Drives in the Possession', options, index=0)
            if num_drives != 'At least 1':
                indices = possessions_df[possessions_df['# Drives'] == int(num_drives)].index.values
                data = data[data['Transition Index'].isin(indices)]
        with col2_2:
            # # of defenders passed on a drive
            options = np.append(['Any'], np.arange(0,6))
            def_passed= st.selectbox('Number of Defenders the Ball Passed', options, index=0)
            if def_passed != 'Any':
                data = data[data['# Defenders Passed'] == int(def_passed)]
    
        #Sliders
        #minimum drive distance:
        min_drive_dist = st.slider('Minimum Drive Distance', key='min dist 2')
        data = data[data['Drive Distance'] >= min_drive_dist]
        
        st.markdown('Series: ' + selections['Series'])
        st.markdown('Game: ' + selections['Game'])
        st.markdown('Player: ' + selections['Driver'])
        st.markdown('Transition initiated by: ' + selections['Trigger'])
        st.markdown('Outcome: ' + selections['Outcome'])
        
    with col2: #COURT
        show_drives = st.checkbox('Click to show Drives')
        plt.style.use('dark_background')
        fig2 = plt.figure(figsize=(12, 7))

        center_coord_x = 0
        center_coord_y = 0
        ax = make_fig(cc_x=center_coord_x, cc_y=center_coord_y)
        plt.xlim(center_coord_x-50, center_coord_x+50)
        plt.ylim(center_coord_y-30, center_coord_y+30)

        if show_drives:
            for idx in data.index.values:
                try:
                    x = data['Drive Start'].loc[idx][0]
                    y = data['Drive Start'].loc[idx][1]
                    dx = data['Drive End'].loc[idx][0] - x
                    dy = data['Drive End'].loc[idx][1] - y
                    if np.isnan(data['OutcomeMSG'].loc[idx]):
                        c = 'w'
                    elif data['OutcomeMSG'].loc[idx] == 1 or data['OutcomeMSG'].loc[idx] == 6:
                        c = 'r'
                    else:
                        c = '#1f77b4'
                    plt.arrow(x,y,dx,dy, head_width=0.8, color=c)
                except: #ball went out of bounds
                    x = data['Drive Start'].loc[idx][0]
                    y = data['Drive Start'].loc[idx][1]
                    plt.plot(x,y,'ro')      
        ax.set_xticks([])
        ax.set_yticks([])
        st.pyplot(fig2)  
    return data
    
    
def display2(data):
    '''
    STATISTICS FOR CURRENT SELECTION
    '''
    st.subheader('Stats For Current Selection')
    num_drives = len(data)
    try:
        ave_dist = round(sum(data['Drive Distance'].values)/num_drives,2) 
    except ZeroDivisionError:
        ave_dist = '-'
        
    #assume each free throw opportunity ended in 1.5 points (75% free throw average estimate)
    ppp = get_ppp(data)
    num_possessions = len(np.unique(data['Transition Index'].values))
    shots_data = data[data['OutcomeMSG'].isin([1,2,6])]
    num_shots = len(np.unique(shots_data['Transition Index'].values))
    try:
        perc_shots = num_shots / num_possessions
        perc_shots = str(round(perc_shots*100,1)) + '%'
    except ZeroDivisionError:
        perc_shots = '-'

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric('Average Drive Distance', ave_dist)
    with col2:
        st.metric('Number of Possessions', num_possessions)
    with col3:
        st.metric('Points per possession*', ppp)
    with col4:
        st.metric('Number of Shots', num_shots)
    with col5:
        st.metric('% of Possessions Ending in a Shot', perc_shots)
    st.markdown("*When possessions that did not end in a transition shot are included, PPP will be uncharacteristically low as these possessions would be considered 0 points")



def display3(data, original_data):
    '''
    TEAM BREAKDOWNS
    '''
    st.header('Team Breakdowns')
    
    col1, col2 = st.columns(2)
    with col1:
        button1 = st.button('Show Defenders Passed Charts')
    with col2:
        button2 = st.button('Show Points Per Possession Charts')
    
    def_passed_means_team = data.groupby(['Team Name'])['# Defenders Passed'].mean()
    def_passed_sums_team = data.groupby(['Team Name'])['# Defenders Passed'].sum()
    num_drives_team = data.groupby(['Team Name'])['# Defenders Passed'].count()
    num_games = get_num_games(data)
    
    if button1: #DEFENDERS PASSED
        col1, col2 = st.columns(2)
        
        with col1: #MEAN DEFENDERS PASSED
            fig = px.bar(x = def_passed_means_team.index, y = def_passed_means_team.values)
            fig.update_layout(width=600, height=500,  
                            title='Mean Defenders Passed Per Drive', title_x=0.25,
                            xaxis_title="Team",
                            yaxis_title="") 
            st.plotly_chart(fig)
        
        with col2: # TOTAL NUMBER OF DEFENDERS PASSED
            num_def_passed_per_game = [def_passed_sums_team[x]/num_games[x] for x in def_passed_sums_team.index]
            
            fig = px.bar(x = def_passed_sums_team.index, y = num_def_passed_per_game)
            fig.update_layout(width=600, height=500,  
                            title='# of Defenders Passed on Transition Drives Per Game', title_x=0.2,
                            xaxis_title="Team",
                            yaxis_title="") 
            st.plotly_chart(fig)

        col1, col2, col3 = st.columns([25,60,15])
        with col2: #MEAN VS TOTAL
            num_drives_per_game = [num_drives_team[x]/num_games[x] for x in num_drives_team.index]
            fig = px.scatter(x = num_drives_per_game, y = def_passed_means_team.values, text = def_passed_sums_team.index)
            fig.update_layout(width=600, height=400,  
                            title='Mean Defenders Passed vs # of Drives Per Game', title_x=0.25,
                            xaxis_title="Numer of Transition Drives Per Game",
                            yaxis_title='Mean Defenders Passed') 
            fig.update_traces(marker=dict(size=10), textposition='top center')
            fig.update_xaxes(range=[min(num_drives_per_game)-5, max(num_drives_per_game)+5])
            fig.update_yaxes(range=[min(def_passed_means_team)-0.02, max(def_passed_means_team)+0.03])
            st.plotly_chart(fig)
        
    if button2:
        col1, col2 = st.columns(2)
        with col1: #PPP BASED ON MIN # OF DEFENDERS PASSED ON A PASS    
            ppp_df = get_ppp_df(data, 0, 6, '# Defenders Passed')
            colors = {'Boston Celtics': 'green', 'Dallas Mavericks': 'blue', 'Golden State Warriors': 'gold', 'Miami Heat': 'red'}
            color_to_plot = [colors[c] for c in colors if c in ppp_df.columns]
            
            fig = px.line(ppp_df, x=ppp_df.index, y=ppp_df.columns, color_discrete_sequence=color_to_plot)
            fig.update_layout(width=600, height=400,  
                            xaxis_title="# of Defenders Passed", 
                            yaxis_title="Points Per Possession", 
                            legend_title=None) 
            st.plotly_chart(fig)
        
        with col2: #PPP BASED ON MIN DISTANCE OF PASS
            ppp_df2 = get_ppp_df(data, int(min(data['Drive Distance'].values)), int(max(data['Drive Distance'].values)), 'Drive Distance')
            to_plot2 = [v for v in list(ppp_df2.columns)]
            color_to_plot2 = [colors[c] for c in colors if c in to_plot2]
            
            fig2 = px.line(ppp_df2, x=ppp_df2.index, y=ppp_df2.columns, color_discrete_sequence=color_to_plot2)
            fig2.update_layout(width=600, height=400,  
                               xaxis_title="Minimum Drive Distance", 
                               yaxis_title='Points Per Possession',
                               legend_title=None) 
            st.plotly_chart(fig2)
        
        
def display4(data):  
    '''
    PLAYER BREAKDOWNS
    ''' 
    st.header('Player Breakdowns') 
    
    num_games_dict = get_num_games_player(data, 'Driver') #dictionary containing number of games played for each player
    players = np.array(list(num_games_dict.keys())) #get list of players
    num_games = list(num_games_dict.values())
    
    num_drives_player = data.groupby(['Driver'])['# Defenders Passed'].count() #total number of drives made in transition
    num_drives_per_game = [round(num_drives_player[x]/num_games_dict[x],2) for x in num_drives_player.index]
    num_drives_per_game_df = pd.DataFrame({'Player':num_drives_player.index, '# Drives Per Game': num_drives_per_game})
    
    #Sliders
    #minimum drive distance:
    min_drive_dist = st.slider('Minimum Drive Distance', key='min dist 1')
    data = data[data['Drive Distance'] >= min_drive_dist]
    #minimum number of drives per game:
    min_num_drives = st.slider('Minimum Number of Transition Drives Per Game for a Single Player', min_value=0, max_value=int(max(np.round(num_drives_per_game_df['# Drives Per Game'].values))))
    num_drives_per_game_df = num_drives_per_game_df[num_drives_per_game_df['# Drives Per Game'] >= min_num_drives]
    data = data[data['Driver'].isin(num_drives_per_game_df['Player'].values)]
    #minimum number of games played:
    if max(num_games) > 1:
        min_num_games = st.slider('Minimum Number of Games Played', min_value=1, max_value=max(num_games))
        min_games_indices = np.where(np.array(num_games)>=min_num_games) #get indices of players who played in min_num_games
        eligible_players = players[min_games_indices] #get player names of those who played in min_num_games
        data = data[data['Driver'].isin(eligible_players)] #keep the data only for the players who played in min_num_games
        

    def_passed_means_player = data.groupby(['Driver'])['# Defenders Passed'].mean() #number of defenders passed per drive in transition on average
    speed_means_player = data.groupby(['Driver'])['Speed'].mean()
    
    #MEAN DEFENDERS 
    col1, col2, col3 = st.columns(3)
    with col1:
        button3 = st.button('Show Defenders Passed Visualizations', key='drive_3')
    with col2:
        button4 = st.button('Show Speed Visualizations', key='drive_4')
    with col3:
        button6 = st.button('Show Points per Possession', key='drive_6')
      
       
    if button3: #DEFENDERS PASSED
        zipped_pairs = zip(def_passed_means_player.values, def_passed_means_player.index)
        sorted_mean_list = sorted(def_passed_means_player.values, reverse=True)
        sorted_player_list = [x for _, x in sorted(zipped_pairs, reverse=True)]

        #MEAN DEFENDERS PASSED PER DRIVE
        fig = px.bar(x = sorted_player_list, y = sorted_mean_list)
        fig.update_layout(width=1200, height=500,  
                        title='Mean Defenders Passed On a Transition Drive', title_x=0.35,
                        xaxis_title="Player",
                        yaxis_title="") #template='plotly_dark',
        st.plotly_chart(fig)
        
        #TOTAL NUMBER OF DRIVES PER GAME VS MEAN DEFENDERS PASSED
        filtered_num_drives_player = data.groupby(['Driver'])['# Defenders Passed'].count() #total number of drives made in transition
        filtered_num_drives_per_game = [round(filtered_num_drives_player[x]/num_games_dict[x],2) for x in filtered_num_drives_player.index]
        fig2 = px.scatter(x = filtered_num_drives_per_game, y = def_passed_means_player.values, text = def_passed_means_player.index)
        fig2.update_layout(width=1200, height=700,  
                        title='Mean Defenders Passed on the Drive vs Number of Drives', title_x=0.35,
                        xaxis_title="# of Transition Drives Per Game", yaxis_title='Mean Defenders Passed') #template='plotly_dark',
        fig2.update_traces(textposition='top center', marker=dict(size=10))
        st.plotly_chart(fig2)
    
    if button4: #DRIVE SPEED
        zipped_pairs = zip(speed_means_player.values, speed_means_player.index)
        sorted_speed_list = sorted(speed_means_player.values, reverse=True)
        sorted_player_list = [x for _, x in sorted(zipped_pairs, reverse=True)]

        #MEAN DRIVE SPEED
        fig3 = px.bar(x = sorted_player_list, y = sorted_speed_list)
        fig3.update_layout(width=1200, height=500,  
                        title='Mean Speed On a Transition Drive', title_x=0.4,
                        xaxis_title="Player",
                        yaxis_title="feet/second") 
        fig3.update_yaxes(range=[min(sorted_speed_list)-1, max(sorted_speed_list)+1])
        st.plotly_chart(fig3)
        
        #SPEED BOX CHART
        fig4 = px.box(data, x='Driver', y='Speed')
        fig4.update_layout(width=1200, height=500, 
                           title='Drive Speed', 
                           xaxis_title='Player',
                           yaxis_title="feet/second") 
        st.plotly_chart(fig4)
        
    if button6: #TEAM PPP BASED ON A PLAYERS DRIVE CHARACTERISTICS     
        st.markdown('#')
        st.markdown('The chart below shows the teams points per possession when a certain player drives the ball at least once in a transition possession. Use the filters above and on the sidebar to include desired pool of players and play types.')

        ppp_df = get_ppp_player_df(data, 'Driver')
        ppp_df_sorted = ppp_df.sort_values('Points per Possession', ascending=False).reset_index()
        
        colors = {'Boston Celtics': 'green', 'Dallas Mavericks': 'blue', 'Golden State Warriors': 'gold', 'Miami Heat': 'red'}
        fig = px.bar(ppp_df_sorted, x=ppp_df_sorted.index, y='Points per Possession', color='Team', color_discrete_map=colors)
        fig.update_layout(width=1200, 
                          height=500,  
                          xaxis_title="Player",
                          xaxis = dict(tickmode='array', tickvals = ppp_df_sorted.index, ticktext = ppp_df_sorted['Player']),
                          yaxis_title="Points Per Possession", 
                          legend_title=None) 
        st.plotly_chart(fig)
        
        #SPEED OF DRIVE VS MEAN DEFENDERS PASSED WITH PPP AS DOT SIZE
        fig2 = px.scatter(x = def_passed_means_player.values, 
                          y = speed_means_player.values, 
                          text = speed_means_player.index, 
                          color=ppp_df['Team'], 
                          color_discrete_map=colors, 
                          size=ppp_df['Points per Possession'])
        fig2.update_layout(width=1200, height=700,  
                        title='Mean Drive Speed vs Mean Defenders Passed on the Drive', title_x=0.25,
                        xaxis_title="Mean Defenders Passed", yaxis_title='Mean Speed (feet/sec)',
                        legend_title=None) 
        fig2.update_traces(textposition=improve_text_position(speed_means_player.index))
        st.plotly_chart(fig2)
        st.markdown("**Size of the marker represents the points per possession produced by the player's drives")
    

def main():
    
    st.title('NBA Transition Tendencies: Driving')
    st.markdown('''The sidebar contains filtering options. These filters apply to ALL sections, metrics, and charts on this page. 
                 Filters on the page (not on the sidebar) are applied only to the charts and metrics contained within that section.
                 Click "Show Definitions" to view descriptions of important metrics and terms, such as how a transition possession was defined.''')
    
    show_defs = st.checkbox('Show Definitions', key='drive definitions')
    if show_defs:
        definitions = pd.DataFrame({'Metric': ['Transition Possession', 'Transition Initiated By', 'Transition Outcome', 'Drive', 'Drive Distance', 'Drive Speed', 'Number of Drives in a Possession', 'Number of Defenders the Ball Passed', 'Points per Possession'],
                                    'Definition': ['The first 8 seconds of a possession after a team has forced a turnover, gathered a defensive rebound, or inbounded the ball after being scored on',
                                                   'How the transition opportunity was initiated, determined to be off of defensive rebounds or the other teams turnovers and made shots',                                                   
                                                   'The outcome of the transition possession (no shot, shot, non-shooting foul, stoppage, turnover). "No shot" means there was no shot within the first 8 seconds after gaining possession. "Shot" means either a shot was taken or a shooting foul was comitted. A "stoppage" means the clock stopped but the offensive team retained possession.',
                                                   'Any time a player took at least one dribble', 
                                                   'The euclidean distance (in feet) between the points where the player first touched the ball and last touch the ball',
                                                   'The total euclidean distance (in feet) of a drive (sum of distances between each recorded location of the drive) divided by the length of the drive (in seconds)',
                                                   'The number of times in a possession a player took at least one dribble when they possessed the ball',
                                                   'The number of defenders who started ahead of the ball at the start of the drive and ended behind the ball at the end of the drive',
                                                   'Calculated as [3*(# of three point field goals) + 2*(# of two point field goals) + 1.5*(# of shooting fouls)] / (# of possessions). Because possessions that did not result in a shot in the first 8 seconds are included, this metric is skewed to be smaller than normal when including possessions with no shot. Only possessions with at least 1 pass are included in the calculation.']
                                    }) 

        st.markdown(definitions.style.hide(axis="index").to_html(), unsafe_allow_html=True)
    
    drive_df = load_data('data/transition/drive_stats.pkl')
    possessions_df = load_data('data/transition/possession_summaries.pkl')

    drive_df.loc[np.isnan(drive_df['# Defenders Passed']), '# Defenders Passed'] = np.nan
    drive_df['Speed'] = round(drive_df['Total Drive Distance']/drive_df['Drive Length (sec)'], 2)
    drive_df.loc[drive_df['Transition Trigger'] == 'SHOT', 'Transition Trigger'] = "Made Shot"
    drive_df.loc[drive_df['Transition Trigger'] == 'REB', 'Transition Trigger'] = "Defensive Rebound"
    drive_df.loc[drive_df['Transition Trigger'] == 'TO', 'Transition Trigger'] = "Turnover"
    drive_df.loc[drive_df['Outcome'] == 'foul', 'Outcome'] = "non-shooting foul"

    
    show_raw_data, drive_data, selections = create_sidebar(drive_df) 
    
    drive_data_selected_team = display1(drive_data, possessions_df, selections)
    
    display2(drive_data_selected_team)
    
    st.markdown('#')
    display3(drive_data, drive_df)
    
    st.markdown('#')
    st.markdown('#')
    display4(drive_data)
    
    
    if show_raw_data:
        st.subheader('Raw data')
        st.write(drive_data)
main()
