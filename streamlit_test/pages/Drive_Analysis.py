import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import sys
 
# adding Folder_2/subfolder to the system path
sys.path.append('/Users/emmaritcey/Documents/basketball_research/wisd-hackathon')
from src.visualization.draw_court import make_fig
from helpers import load_data, create_selectbox, get_num_games, get_ppp, get_ppp_df, get_num_games_player
st.set_page_config(layout="wide")

st.title('NBA Transition Tendencies: Driving')


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

    #hist_vals, bin_edges = np.histogram(df['# Defenders Passed'].values, bins=np.arange(-1,7))
    # fig = px.histogram(data, x="# Defenders Passed")
    # st.write(fig)
    col1, col2 = st.columns([1,3])
    
    with col1:
        show_drives = st.checkbox('Show Drives')
        if show_drives:
            st.subheader('Displaying Drives for:')
            team_selection, data = create_selectbox(data, 'Team Name', 'Team:', False)
            
            # col1_2, col2_2 = st.columns(2)
            # with col1_2:
            #NUMBER INCREMENTS
            #minimum # of passes in a possession
            # num_drives = st.number_input('Number of Drives in the Possession', min_value=1, max_value=max(possessions_df['# Drives'].values), step=1)
            # indices = possessions_df[possessions_df['# Drives']==num_drives].index.values
            # data = data[data['Transition Index'].isin(indices)]
            # with col2_2:
            #     #minimum # of defenders passed on a drive
            #     def_passed = st.number_input('Number of Defenders the Ball Passed', min_value=0, max_value=5, step=1)
            #     data = data[data['# Defenders Passed'] == def_passed]
                
            col1_2, col2_2 = st.columns(2)
            with col1_2:
                #Number Increments
                #minimum # of passes in a possession
                options = np.append(['Any'], sorted(possessions_df['# Drives'].unique())[1:])
                num_drives = st.selectbox('Number of Drives in the Possession', options, index=0)
                if num_drives != 'Any':
                    indices = possessions_df[possessions_df['# Drives'] == int(num_drives)].index.values
                    data = data[data['Transition Index'].isin(indices)]
            #data   
            with col2_2:
                #minimum # of defenders passed on a pass
                options = np.append(['Any'], np.arange(0,6))
                def_passed= st.selectbox('Number of Defenders the Ball Passed', options, index=0)
                #min_def_passed = st.number_input('Min # of Defenders the Ball Passed', min_value=0, max_value=5, step=1)
                if def_passed != 'Any':
                    data = data[data['# Defenders Passed'] == int(def_passed)]
                
                
                
            #Sliders
            #minimum drive distance:
            min_drive_dist = st.slider('Minimum Drive Distance')
            data = data[data['Drive Distance'] >= min_drive_dist]
            
            st.text('Series: ' + selections['Series'])
            st.text('Game: ' + selections['Game'])
            st.text('Player: ' + selections['Driver'])
            st.text('Transition initiated by: ' + selections['Trigger'])
            st.text('Outcome: ' + selections['Outcome'])

    with col2:
        fig2 = plt.figure(figsize=(12, 7))

        center_coord_x = 0
        center_coord_y = 0
        ax = make_fig(cc_x=center_coord_x, cc_y=center_coord_y)
        #plt.scatter(x_locs, y_locs, c=temp_df['shotClock'],
        #            cmap=plt.cm.Blues, s=100, zorder=1)

        plt.xlim(center_coord_x-50, center_coord_x+50)
        plt.ylim(center_coord_y-30, center_coord_y+30)
        #plt.show()

        #TODO: write code to connect pass_df rows to event/tracking data in possessions_tracking_data
        #TODO: add a link to corresponding event video if possible
        #TODO: figure out why when team = Boston, min # passes = 4, the fourth pass doesn't show up
        if show_drives:
            for idx in data.index.values:
                try:
                    #st.write('yes')
                    x = data['Drive Start'].loc[idx][0]
                    y = data['Drive Start'].loc[idx][1]
                    dx = data['Drive End'].loc[idx][0] - x
                    dy = data['Drive End'].loc[idx][1] - y
                    if np.isnan(data['OutcomeMSG'].loc[idx]):
                        c = 'k'
                    elif data['OutcomeMSG'].loc[idx] == 1 or data['OutcomeMSG'].loc[idx] == 6:
                        c = 'r'
                    else:
                        c = 'b'
                    plt.arrow(x,y,dx,dy, head_width=1, color=c)
                except:
                    x = data['Drive Start'].loc[idx][0]
                    y = data['Drive Start'].loc[idx][1]
                    plt.plot(x,y,'ro')      
        
        st.pyplot(fig2)  
    return data
    
def display2(data):
    st.subheader('Stats For Current Selection')
    ave_dist = round(sum(data['Drive Distance'].values)/len(data['Drive Distance']),2) 
    
    #assume each free throw opportunity ended in 1.5 points (75% free throw average estimate)
    ppp = get_ppp(data)
    
    num_possessions = len(data)
    num_shots = len(data[data['OutcomeMSG'].isin([1,2,79])])
    perc_shots = round(num_shots / num_possessions, 2)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric('Average Drive Distance', ave_dist)
    with col2:
        st.metric('Number of Possessions', num_possessions)
    with col3:
        st.metric('Points per possession', ppp)
    with col4:
        st.metric('Number of Shots', num_shots)
    with col5:
        st.metric('% of Possessions Ending in a Shot', str(round(perc_shots*100,1))+'%')


def display3(data, original_data):
    st.header('Team Breakdowns')
    
    col1, col2 = st.columns(2)
    with col1:
        button1 = st.button('Show Defenders Passed Charts')
    with col2:
        button2 = st.button('Show Ponts Per Possession Charts')
    
    def_passed_means_team = data.groupby(['Team Name'])['# Defenders Passed'].mean()
    def_passed_sums_team = data.groupby(['Team Name'])['# Defenders Passed'].sum()
    num_drives_team = data.groupby(['Team Name'])['# Defenders Passed'].count()
    num_games = get_num_games(data)
    
    if button1:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(x = def_passed_means_team.index, y = def_passed_means_team.values)
            fig.update_layout(width=750, height=500,  
                            title='Mean Defenders Passed on Transition Drives', title_x=0.3,
                            xaxis_title="Team") #template='plotly_dark',
            #fig.update_traces(marker=dict(size=10))
            #fig.update_yaxes(range=[min(def_passed_means_team)-0.02, max(def_passed_means_team)+0.01])
            st.plotly_chart(fig)
        
        with col2:
            num_games = get_num_games(original_data)
            num_def_passed_per_game = [def_passed_sums_team[x]/num_games[x] for x in def_passed_sums_team.index]
            
            fig = px.bar(x = def_passed_sums_team.index, y = num_def_passed_per_game)
            fig.update_layout(width=750, height=500,  
                            title='# of Defenders Passed on Transition Drives Per Game', title_x=0.2,
                            xaxis_title="Team") #template='plotly_dark',
            #fig.update_traces(marker=dict(size=10))
            #fig.update_yaxes(range=[min(def_passed_means_team)-0.02, max(def_passed_means_team)+0.01])
            st.plotly_chart(fig)

        num_drives_per_game = [num_drives_team[x]/num_games[x] for x in num_drives_team.index]
        fig = px.scatter(x = num_drives_per_game, y = def_passed_means_team.values, text = def_passed_sums_team.index)
        fig.update_layout(width=600, height=400,  
                        title='Mean Defenders Passed vs # of Drives Per Game', title_x=0.3,
                        xaxis_title="Numer of Drives Per Game",
                        yaxis_title='Mean Defenders Passed') #template='plotly_dark',
        fig.update_traces(marker=dict(size=10), textposition='top center')
        fig.update_xaxes(range=[min(num_drives_per_game)-5, max(num_drives_per_game)+5])
        fig.update_yaxes(range=[min(def_passed_means_team)-0.02, max(def_passed_means_team)+0.03])
        st.plotly_chart(fig)
    
    if button2:
        col1, col2 = st.columns(2)
        with col1:
            #PLOT PPP BASED ON MIN # OF DEFENDERS PASSED ON A PASS    
            ppp_df = get_ppp_df(data, 0, 6, '# Defenders Passed')
            #to_plot = [v for v in list(ppp_df.columns)]
            colors = {'Boston Celtics': 'green', 'Dallas Mavericks': 'blue', 'Golden State Warriors': 'gold', 'Miami Heat': 'red'}
            color_to_plot = [colors[c] for c in colors if c in ppp_df.columns]
            
            fig = px.line(ppp_df, x=ppp_df.index, y=ppp_df.columns, color_discrete_sequence=color_to_plot)
            fig.update_layout(width=600, height=400,  
                            xaxis_title="Minimum # Defenders Passed", 
                            yaxis_title="Points Per Possession", 
                            legend_title=None) #template='plotly_dark',
            #fig.update_traces(marker=dict(size=10))
            #fig.update_yaxes(range=[min(def_passed_means_team)-0.02, max(def_passed_means_team)+0.01])
            st.plotly_chart(fig)
        
        with col2:
            #PLOT PPP BASED ON MIN DISTANCE OF PASS
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
    st.header('Player Breakdowns') 
    
    num_games = get_num_games_player(data, 'Driver')
    
    num_drives_player = data.groupby(['Driver'])['# Defenders Passed'].count() #total number of drives made in transition
    num_drives_per_game = [round(num_drives_player[x]/num_games[x],2) for x in num_drives_player.index]
    num_drives_per_game_df = pd.DataFrame({'Player':num_drives_player.index, '# Drives Per Game': num_drives_per_game})

    #Sliders
    #minimum drive distance:
    min_drive_dist = st.slider('Minimum Drive Distance 1')
    data = data[data['Drive Distance'] >= min_drive_dist]
    #minimum number of drives per game:
    min_num_drives = st.slider('Minimum Number of Transition Drives Per Game for a Single Player', min_value=0, max_value=int(max(np.round(num_drives_per_game_df['# Drives Per Game'].values))))
    num_drives_per_game_df = num_drives_per_game_df[num_drives_per_game_df['# Drives Per Game'] >= min_num_drives]
    data = data[data['Driver'].isin(num_drives_per_game_df['Player'].values)]

    def_passed_means_player = data.groupby(['Driver'])['# Defenders Passed'].mean() #number of defenders passed per drive in transition on average
    def_passed_sums_player = data.groupby(['Driver'])['# Defenders Passed'].sum() #total number of defenders passed in transition from all drives
    
    speed_means_player = data.groupby(['Driver'])['Speed'].mean()
    
    #num_drives_per_game
    
    
    #MEAN DEFENDERS PASSED
    col1, col2, col3 = st.columns(3)
    with col1:
        button3 = st.button('Show Defenders Passed Visualizations')
    with col2:
        button4 = st.button('Show Speed Visualizations')
    with col3:
        button5 = st.button('Show Speed vs Defenders Passed')
       
    if button3:
        zipped_pairs = zip(def_passed_means_player.values, def_passed_means_player.index)
        sorted_mean_list = sorted(def_passed_means_player.values, reverse=True)
        sorted_player_list = [x for _, x in sorted(zipped_pairs, reverse=True)]

        fig = px.bar(x = sorted_player_list, y = sorted_mean_list)
        fig.update_layout(width=1200, height=500,  
                        title='Mean Defenders Passed On a Transition Drive', title_x=0.4,
                        xaxis_title="Player") #template='plotly_dark',
        #fig.update_traces(marker=dict(size=8))
        #fig.update_traces(textfont_size=11, marker=dict(size=10), textposition=improve_text_position(df['reb']))
        st.plotly_chart(fig)
        
        #TOTAL NUMBER OF PASSES PER GAME VS MEAN DEFENDERS PASSED
        filtered_num_drives_player = data.groupby(['Driver'])['# Defenders Passed'].count() #total number of drives made in transition
        filtered_num_drives_per_game = [round(filtered_num_drives_player[x]/num_games[x],2) for x in filtered_num_drives_player.index]
        fig2 = px.scatter(x = def_passed_means_player.values, y = filtered_num_drives_per_game, text = def_passed_means_player.index)
        fig2.update_layout(width=1200, height=700,  
                        title='Number of Drives vs Mean Defenders Passed on the Drive', title_x=0.35,
                        xaxis_title="Mean Defenders Passed", yaxis_title='# of Drives Per Game') #template='plotly_dark',
        fig2.update_traces(textposition='top center', marker=dict(size=8))
        #fig.update_traces(textfont_size=11, marker=dict(size=10), textposition=improve_text_position(df['reb']))
        st.plotly_chart(fig2)
    
    if button4:
        #MEAN DRIVE SPEED
        zipped_pairs = zip(speed_means_player.values, speed_means_player.index)
        sorted_speed_list = sorted(speed_means_player.values, reverse=True)
        sorted_player_list = [x for _, x in sorted(zipped_pairs, reverse=True)]

        fig3 = px.bar(x = sorted_player_list, y = sorted_speed_list)
        fig3.update_layout(width=1200, height=500,  
                        title='Mean Speed On a Transition Drive', title_x=0.4,
                        xaxis_title="Player",
                        yaxis_title="feet/second") #template='plotly_dark',
        #fig3.update_traces(marker=dict(size=8))
        #fig.update_traces(textfont_size=11, marker=dict(size=10), textposition=improve_text_position(df['reb']))
        st.plotly_chart(fig3)
        
        #SPEED BOX CHART
        fig4 = px.box(data, x='Driver', y='Speed')
        fig4.update_layout(width=1200, height=500, 
                           title='Drive Speed', 
                           xaxis_title='Player',
                           yaxis_title="feet/second") 
        #plt.xticks(rotation=90)
        st.plotly_chart(fig4)
        
    if button5:
        #SPEED OF DRIVE VS MEAN DEFENDERS PASSED
        fig2 = px.scatter(x = def_passed_means_player.values, y = speed_means_player.values, text = speed_means_player.index)
        fig2.update_layout(width=1200, height=700,  
                        title='Mean Drive Speed vs Mean Defenders Passed on the Drive', title_x=0.35,
                        xaxis_title="Mean Defenders Passed", yaxis_title='Mean Speed (feet/sec)') #template='plotly_dark',
        fig2.update_traces(textposition='top center', marker=dict(size=8))
        #fig.update_traces(textfont_size=11, marker=dict(size=10), textposition=improve_text_position(df['reb']))
        st.plotly_chart(fig2)
    

#TODO: create visualizations for PPP of each player
#TODO: create visualizations based on possession outcomes
def main():
    drive_df = load_data('data/transition/drive_stats.pkl')
    possessions_df = load_data('data/transition/possession_summaries.pkl')
    
    drive_df.loc[np.isnan(drive_df['# Defenders Passed']), '# Defenders Passed'] = np.nan
    drive_df['Speed'] = round(drive_df['Total Drive Distance']/drive_df['Drive Length (sec)'], 2)
    drive_df.loc[drive_df['Transition Trigger'] == 'SHOT', 'Transition Trigger'] = "MADE SHOT"
    
    show_raw_data, drive_data, selections = create_sidebar(drive_df) 
    
    drive_data = display1(drive_data, possessions_df, selections)
    
    display2(drive_data)
    
    st.markdown('#')
    display3(drive_data, drive_df)
    
    display4(drive_data)
    
    
    if show_raw_data:
        st.subheader('Raw data')
        st.write(drive_data)
main()