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
from helpers import load_data, create_selectbox, get_num_games, get_ppp, get_ppp_df, get_ppp_player_df, improve_text_position, get_value
st.set_page_config(layout="wide")


def cluster_data(data):

    pass_start_x = [x[0] for x in data['Pass Start']]
    pass_start_y = [x[1] for x in data['Pass Start']]

    pass_end_x = [x[0] for x in data['Pass End']]
    pass_end_y = [x[1] for x in data['Pass End']]

    pass_dict = {'Pass Start X': pass_start_x, 'Pass Start Y': pass_start_y, 'Pass End X': pass_end_x, 'Pass End Y': pass_end_y}
    df = pd.DataFrame(pass_dict)
    
    kmeans = KMeans(n_clusters=10, init='random', n_init='auto', random_state=3)
    kmeans.fit(df)
    init_clusters = kmeans.predict(df)
    
    cluster_dict = {0: 4, 1: 0, 2: 7, 3: 5, 4: 8, 5: 2, 6: 9, 7: 3, 8: 1, 9: 6}
    pass_clusters = [cluster_dict[i] for i in init_clusters]
    
    cluster_names_dict =  {0:'Short Outlet, Right', 1:'Short Outlet, Left', 2:'Long Outlet, Right', 
                           3:'Long Outlet, Left', 4:'Hit Ahead, Right', 5:'Hit Ahead, Left', 
                           6:'Swing Pass, Right', 7:'Swing Pass, Left',
                           8: 'Attacking Pass, Right', 9: 'Attacking Pass, Left'}
    cluster_names = [cluster_names_dict[i] for i in pass_clusters]
    
    data['Pass Clusters'] = pass_clusters
    data['Pass Cluster Name'] = cluster_names
    
    return data


def create_sidebar(df):
    #Selection Boxes
    series_selection, data = create_selectbox(df, 'Series', 'Series:')
    game_selection, data = create_selectbox(data, 'Game Title', 'Game:')
    team_selection, data = create_selectbox(data, 'Team Name', 'Team:')
    passer_selection, data = create_selectbox(data, 'Passer', 'Passes Made By:')
    trigger_selection, data = create_selectbox(data, 'Transition Trigger', 'Transition Initiated By:')
    outcome_selection, data = create_selectbox(data, 'Outcome', 'Transition Outcome:')

    selections = {'Series': series_selection, 'Game': game_selection, 'Team': team_selection, 'Passer': passer_selection,
                'Trigger': trigger_selection, 'Outcome': outcome_selection}

    #Check boxes
    show_raw_data = st.sidebar.checkbox('Show Raw Data')

    return show_raw_data, data, selections


def display1(data, possessions_df, selections):
    '''
    Court and passes figure with extra widgets
    '''

    st.header('Overview of Passes')
    st.markdown('- Passes that belong to possessions that ended in a :red[**MADE SHOT**] within the first 8 seconds of the shot clock are represented by :red[**RED**] arrows')
    st.markdown('- Passes that belong to possessions that ended in a :blue[**MISSED SHOT**] within the first 8 seconds of the shot clock are represented by :blue[**BLUE**] arrows')
    st.markdown('- Passes that belong to possessions that ended in **NO SHOT** within the first 8 seconds of the shot clock are represented by **WHITE** arrows')
    
    col1, col2 = st.columns([1,3])
    
    with col1:
        

        st.subheader('Displaying Passes for:')
        
        pass_type, data = create_selectbox(data, 'Pass Cluster Name', 'Pass Type', False)
        
        col1_2, col2_2 = st.columns(2)
        with col1_2:
            #Number Increments
            #minimum # of passes in a possession
            options = np.append(['At least 1'], sorted(possessions_df['# Passes'].unique())[1:])
            num_passes = st.selectbox('Number of Passes in the Possession', options, index=0)
            if num_passes != 'At least 1':
                indices = possessions_df[possessions_df['# Passes'] == int(num_passes)].index.values
                data = data[data['Transition Index'].isin(indices)]
        with col2_2:
            #minimum # of defenders passed on a pass
            options = np.append(['Any'], np.arange(0,6))
            def_passed= st.selectbox('Number of Defenders the Ball Passed', options, index=0)
            #min_def_passed = st.number_input('Min # of Defenders the Ball Passed', min_value=0, max_value=5, step=1)
            if def_passed != 'Any':
                data = data[data['# Defenders Passed'] == int(def_passed)]
        
        #Sliders
        #minimum pass distance:
        min_pass_dist = st.slider('Minimum Pass Distance')
        data = data[data['Pass Distance'] >= min_pass_dist]            
        
        st.markdown('Series: ' + selections['Series'])
        st.markdown('Game: ' + selections['Game'])
        st.markdown('Team: ' + selections['Team'])
        st.markdown('Player: ' + selections['Passer'])
        st.markdown('Transition initiated by: ' + selections['Trigger'])
        st.markdown('Outcome: ' + selections['Outcome'])
        

    with col2:
        show_passes = st.checkbox('Click to show Passes')
        plt.style.use('dark_background')
        fig2 = plt.figure(figsize=(12, 7))

        center_coord_x = 0
        center_coord_y = 0
        ax = make_fig(cc_x=center_coord_x, cc_y=center_coord_y)
        plt.xlim(center_coord_x-50, center_coord_x+50)
        plt.ylim(center_coord_y-30, center_coord_y+30)

        if show_passes:
            for idx in data.index.values:
                try:
                    x = data['Pass Start'].loc[idx][0]
                    y = data['Pass Start'].loc[idx][1]
                    dx = data['Pass End'].loc[idx][0] - x
                    dy = data['Pass End'].loc[idx][1] - y
                    if np.isnan(data['OutcomeMSG'].loc[idx]):
                        c = 'w'
                    elif data['OutcomeMSG'].loc[idx] == 1 or data['OutcomeMSG'].loc[idx] == 6:
                        c = 'r'
                    else:
                        c = '#1f77b4'
                    plt.arrow(x,y,dx,dy,  head_width=0.8, color=c)
                except: #ball went out of bounds
                    x = data['Pass Start'].loc[idx][0]
                    y = data['Pass Start'].loc[idx][1]
                    plt.plot(x,y,'ro')      
        ax.set_xticks([])
        ax.set_yticks([])
        st.pyplot(fig2)  
            
    return data
            

def display2(data):
    '''
    Statistics for current selection of data
    '''
    
    st.subheader('Stats For Current Selection') 
    num_passes = len(data)
    try:      
        ave_dist = round(sum(data['Pass Distance'].values)/num_passes,2) 
    except ZeroDivisionError:
        ave_dist = '-'

    #get points per possession
    ppp = get_ppp(data)

    num_possessions = len(np.unique(data['Transition Index'].values))
    shots_data = data[data['OutcomeMSG'].isin([1,2,6])]
    num_shots = len(np.unique(shots_data['Transition Index'].values))
    try:
        perc_shots = round(num_shots / num_possessions, 2)
        perc_shots = str(round(perc_shots*100,1))+'%'
    except:
        perc_shots = '-'
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric('Average Pass Distance', ave_dist)
    with col2:
        st.metric('Number of Possessions', num_possessions)
    with col3:
        st.metric('Points per possession*', ppp)
    with col4:
        st.metric('Number of Shots', num_shots)
    with col5:
        st.metric('% of Possessions Ending in a Shot', perc_shots)  
    st.markdown("*When possessions that did not end in a transition shot are included, PPP will be uncharacteristically low as these possessions would be considered 0 points")
        
        
def show_clusters(data):
    st.header('Pass Types')
    st.markdown('K-means clustering was performed using k=7 to get 7 different types of passes based on their start and end location.')
    show_pass_clusters = st.checkbox('Click to Show Passes by Cluster')
    
    if show_pass_clusters:
        color_dict = {0: 'b', 1: 'r', 2: 'g', 3: 'm', 4: 'y', 5: 'c', 6: 'w', 7: 'tab:orange',
                      8: 'tab:purple', 9: 'tab:pink'}

        titles = ['Short Outlet, Right', 'Short Outlet, Left', 'Long Outlet, Right', 'Long Outlet, Left', 'Hit Ahead, Right', 'Hit Ahead, Left', 
                  'Swing Pass, Right', 'Swing Pass, Left', 'Attacking Pass, Right', 'Attacking Pass, Left']
        plt.style.use('dark_background')
        n_rows = 5
        n_cols = 2
        fig, axs = plt.subplots(n_rows, n_cols, figsize=(12, 16))
        #fig.delaxes(axs[3,1])
        
        center_coord_x = 0
        center_coord_y = 0
        
        total_num_passes = len(data)
        perc_passes_dict = {}
        ppp_dict = {}
        cluster_num = 0
        for row in range(0, n_rows):
            for col in range(0, n_cols):
                curr_data = data[data['Pass Clusters']==cluster_num]
                perc_passes = round(len(curr_data)/total_num_passes*100,2)
                perc_passes_dict[titles[cluster_num]] = perc_passes
                ppp = get_ppp(curr_data)
                ppp_dict[titles[cluster_num]] = ppp
                axs[row, col] = make_fig(axs[row,col], cc_x=center_coord_x, cc_y=center_coord_y)
                for idx in data.index.values:
                    if data['Pass Clusters'].loc[idx]==cluster_num:
                        #try:
                        x = data['Pass Start'].loc[idx][0]
                        y = data['Pass Start'].loc[idx][1]
                        dx = data['Pass End'].loc[idx][0] - x
                        dy = data['Pass End'].loc[idx][1] - y
                        c = color_dict[data['Pass Clusters'].loc[idx]]
                        axs[row,col].arrow(x,y,dx,dy, head_width=0.8, color=c)
                    axs[row,col].set_xticks([])
                    axs[row,col].set_yticks([])
                axs[row,col].set_title(titles[cluster_num] + ', ' + str(perc_passes) + '%')
                cluster_num += 1
        
        st.pyplot(fig)        

        
def display3(data, original_data):
    '''
    TEAM BREAKDOWNS
    '''
    st.header('Team Breakdowns')
    st.markdown('Select "All" to assess all types of passes')
    cluster_selection, data = create_selectbox(data, 'Pass Cluster Name', 'Pass Type:', sidebar=False)
    
    
    col1, col2 = st.columns(2)
    with col1:
        button1 = st.button('Show Defenders Passed Charts', key='pass_1')
    with col2:
        button2 = st.button('Show Points Per Possession Charts', key='pass2')
    
    def_passed_means_team = data.groupby(['Team Name'])['# Defenders Passed'].mean()
    def_passed_sums_team = data.groupby(['Team Name'])['# Defenders Passed'].sum()
    num_passes_team = data.groupby(['Team Name'])['# Defenders Passed'].count()
    num_games = get_num_games(data, 'Team Name')
    
    if button1: #DEFENDERS PASSED CHARTS
        col1, col2 = st.columns(2)
        with col1: #MEAN DEFENDERS PASSED
            fig = px.bar(x = def_passed_means_team.index, y = def_passed_means_team.values)
            fig.update_layout(width=550, height=500,  
                            title='Mean # of Defenders Passed per Pass', title_x=0.3,
                            xaxis_title="Team",
                            yaxis_title="") #template='plotly_dark',
            st.plotly_chart(fig)
            
        with col2: #MEAN PER PASS vs TOTAL PER GAME
            num_passes_per_game = [num_passes_team[x]/num_games[x] for x in num_passes_team.index]
            fig = px.scatter(x = num_passes_per_game, y = def_passed_means_team.values, text = def_passed_sums_team.index)
            fig.update_layout(width=550, height=500,  
                            title='Mean # of Defenders Passed per Pass vs # of Passes per Game', title_x=0.22,
                            xaxis_title="Numer of Transition Passes Per Game",
                            yaxis_title='Mean Defenders Passed') #template='plotly_dark',
            fig.update_traces(marker=dict(size=10), textposition='top center')
            fig.update_xaxes(range=[max(min(num_passes_per_game)-5,0), max(num_passes_per_game)+5])
            fig.update_yaxes(range=[min(def_passed_means_team)-0.02, max(def_passed_means_team)+0.1])
            st.plotly_chart(fig)
        
    if button2: #POINTS PER POSSESSION
        #colors = {'Boston Celtics': 'green', 'Dallas Mavericks': 'blue', 'Golden State Warriors': 'gold', 'Miami Heat': 'red'}
        #color_to_plot = [colors[c] for c in colors if c in ppp_df.columns]
        
        ppp_pass_types = data.groupby(['Team Name', 'Pass Cluster Name']).apply(get_ppp)
        
        team_list = [x for x,_ in ppp_pass_types.index]
        pass_list = [y for _, y in ppp_pass_types.index]
        ppp_passtype_df = pd.DataFrame({'Team': team_list, 'Pass Type': pass_list, 'Points per Possession': ppp_pass_types.values})

        
        fig = px.bar(ppp_passtype_df, x='Team', y='Points per Possession', color='Pass Type', barmode='group')
        fig.update_layout(width=1100, height=400,  
                        yaxis_title='Points Per Possession',
                        xaxis_title="Team", legend_title=None) #template='plotly_dark',
        st.plotly_chart(fig)
        
        
        col1, col2 = st.columns(2)
        with col1: #PLOT PPP BASED ON MIN # OF DEFENDERS PASSED ON A PASS    
            ppp_df = get_ppp_df(data, 0, 6, '# Defenders Passed')
            #to_plot = [v for v in list(ppp_df.columns)]
            colors = {'Boston Celtics': 'green', 'Dallas Mavericks': 'blue', 'Golden State Warriors': 'gold', 'Miami Heat': 'red'}
            color_to_plot = [colors[c] for c in colors if c in ppp_df.columns]
            
            fig = px.line(ppp_df, x=ppp_df.index, y=ppp_df.columns, color_discrete_sequence=color_to_plot)
            fig.update_layout(width=600, height=400,  
                            yaxis_title='Points Per Possession',
                            xaxis_title="# of Defenders Passed", legend_title=None) #template='plotly_dark',
            st.plotly_chart(fig)
        
        with col2: #PLOT PPP BASED ON MIN DISTANCE OF PASS
            ppp_df2 = get_ppp_df(data, int(min(data['Pass Distance'].values)), int(max(data['Pass Distance'].values)), 'Pass Distance')
            to_plot2 = [v for v in list(ppp_df2.columns)]
            color_to_plot2 = [colors[c] for c in colors if c in to_plot2]
            
            fig2 = px.line(ppp_df2, x=ppp_df2.index, y=ppp_df2.columns, color_discrete_sequence=color_to_plot2)
            fig2.update_layout(width=600, height=400,  
                            yaxis_title='Points Per Possession', 
                            xaxis_title="Minimum Pass Distance", legend_title=None) 
            st.plotly_chart(fig2)

    
def display4(data):
    '''
    PLAYER BREAKDOWNS
    '''
    st.header('Player Breakdowns') 
    
    num_games_dict = get_num_games(data, 'Passer')
    players = np.array(list(num_games_dict.keys())) #get list of players
    num_games = list(num_games_dict.values())
    
    st.markdown('Select "All" to assess all types of passes')
   # cluster_selection, data = create_selectbox(data, 'Pass Cluster Name', 'Pass Type:', sidebar=False, key='pass_type2')
   
    cluster_selection = st.multiselect('Pass Type:', np.append(['All'], sorted(data['Pass Cluster Name'].unique())))
    
    if len(cluster_selection) != 0: 
        if cluster_selection[0] != 'All':
            data = data[data['Pass Cluster Name'].isin(cluster_selection)]
        else:
            data = data
    
        num_passes_player = data.groupby(['Passer'])['# Defenders Passed'].count() #total number of drives made in transition
        num_passes_per_game = [round(num_passes_player[x]/num_games_dict[x],2) for x in num_passes_player.index]
        num_passes_per_game_df = pd.DataFrame({'Player':num_passes_player.index, '# Passes Per Game': num_passes_per_game})
        
        #Sliders
        #minimum number of passes per game:
        min_num_passes = st.slider('Select Minimum Number of Transition Passes Per Game for a Single Player', min_value=0, max_value=int(max(np.round(num_passes_per_game_df['# Passes Per Game'].values))))
        num_passes_per_game_df = num_passes_per_game_df[num_passes_per_game_df['# Passes Per Game'] >= min_num_passes]
        data = data[data['Passer'].isin(num_passes_per_game_df['Player'].values)]
        #minimum number of games played:
        if max(num_games) > 1:
            min_num_games = st.slider('Minimum Number of Games Played', min_value=1, max_value=max(num_games))
            min_games_indices = np.where(np.array(num_games)>=min_num_games) #get indices of players who played in min_num_games
            eligible_players = players[min_games_indices] #get player names of those who played in min_num_games
            data = data[data['Passer'].isin(eligible_players)] #keep the data only for the players who played in min_num_games

        def_passed_means_player = data.groupby(['Passer'])['# Defenders Passed'].mean() #number of defenders passed per pass in transition on average

        #MEAN DEFENDERS 
        col1, col2 = st.columns(2)
        with col1:
            button3 = st.button('Show Defenders Passed Visualizations', key='pass_3')
        with col2:
            button4 = st.button('Show Points per Possession', key='pass_4')
            
        colors = {'Boston Celtics': 'green', 'Dallas Mavericks': 'blue', 'Golden State Warriors': 'gold', 'Miami Heat': 'red'}
        filtered_num_passes_player = data.groupby(['Passer'])['# Defenders Passed'].count() #total number of drives made in transition
        filtered_num_passes_per_game = [round(filtered_num_passes_player[x]/num_games_dict[x],2) for x in filtered_num_passes_player.index]
        
        if button3: #DEFENDERS PASSED
            team_list = data.groupby(['Passer']).agg({'Team Name': get_value})
            
            #MEAN DEFENDERS PASSED PER PASS
            #fig = px.bar(x = sorted_player_list, y = sorted_mean_list, color=sorted_team_list, color_discrete_map=colors)
            fig = px.bar(x = def_passed_means_player.index, y = def_passed_means_player.values, color=team_list['Team Name'], color_discrete_map=colors)
            fig.update_layout(width=1200, height=500,  
                            title='Mean Defenders Passed On a Transition Pass', title_x=0.4,
                            xaxis_title="Player",
                            yaxis_title="",
                            xaxis={'categoryorder':'total descending'},
                            legend_title=None) 
            st.plotly_chart(fig)

            #TOTAL NUMBER OF PASSES PER GAME VS MEAN DEFENDERS PASSED
            fig2 = px.scatter(x = filtered_num_passes_per_game, 
                            y = def_passed_means_player.values, 
                            text = def_passed_means_player.index,
                            color = team_list['Team Name'],
                            color_discrete_map=colors
                            )
            fig2.update_layout(width=1200, height=700,  
                            title='Mean Defenders Passed on the Pass vs Number of Passes', 
                            title_x=0.35,
                            xaxis_title="# of Transition Passes Per Game", 
                            yaxis_title='Mean Defenders Passed',
                            legend_title=None) 
            fig2.update_traces(textposition=improve_text_position(def_passed_means_player.index), marker=dict(size=8))
            st.plotly_chart(fig2)
        
        if button4: #POINTS PER POSSESSION
            st.markdown('#')
            st.markdown('The chart below shows the teams points per possession when a certain player passes the ball at least once in a transition possession. Use the filters above and on the sidebar to include desired pool of players and play types.')
            
            ppp_df = get_ppp_player_df(data, 'Passer')
            ppp_df_sorted = ppp_df.sort_values('Points per Possession', ascending=False).reset_index()
            
            
            fig = px.bar(ppp_df_sorted, x=ppp_df_sorted.index, y='Points per Possession', color='Team', color_discrete_map=colors)
            fig.update_layout(width=1200, height=500,  
                            xaxis_title="Player", 
                            xaxis = dict(tickmode='array', tickvals = ppp_df_sorted.index, ticktext = ppp_df_sorted['Player']),
                            yaxis_title="Points Per Possession", 
                            legend_title=None) 
            st.plotly_chart(fig)
            
            #TOTAL NUMBER OF PASSES PER GAME VS MEAN DEFENDERS PASSED

            fig2 = px.scatter(x = filtered_num_passes_per_game, 
                            y = def_passed_means_player.values, 
                            text = def_passed_means_player.index, 
                            color=ppp_df['Team'], 
                            color_discrete_map=colors, 
                            size=ppp_df['Points per Possession'])
            fig2.update_layout(width=1200, height=700,  
                            title='Mean Defenders Passed on the Pass vs Number of Passes', title_x=0.35,
                            xaxis_title="# of Transition Passes Per Game", yaxis_title='Mean Defenders Passed')
            fig2.update_traces(textposition=improve_text_position(def_passed_means_player.index))
            st.plotly_chart(fig2)
            
            st.markdown("**Size of the marker represents the points per possession produced by the player's passes")
    
        st.write('#')
        st.write('#')
        st.write('#')
        st.write('#')
        st.write('#')
        st.write('#')
        st.write('#')
        st.write('#')

def main():
    st.title('NBA Transition Tendencies: Passing')
    st.markdown('''The sidebar contains filtering options. These filters apply to ALL sections, metrics, and charts on this page. 
                 Filters on the page (not on the sidebar) are applied only to the charts and metrics contained within that section.
                 Click "Show Definitions" to view descriptions of important metrics and terms, such as how a transition possession was defined.''')
    
    show_defs = st.checkbox('Show Definitions', key='pass definitions')
    if show_defs:
        definitions = pd.DataFrame({'Metric': ['Transition Possession', 'Transition Initiated By', 'Transition Outcome', 'Pass Distance', 'Number of Defenders the Ball Passed', 'Points per Possession'],
                                    'Definition': ['The first 8 seconds of a possession after a team has forced a turnover, gathered a defensive rebound, or inbounded the ball after being scored on',
                                                   'How the transition opportunity was initiated, determined to be off of defensive rebounds or the other teams turnovers and made shots',                                                   
                                                   'The outcome of the transition possession (no shot, shot, non-shooting foul, stoppage, turnover). "No shot" means there was no shot within the first 8 seconds after gaining possession. "Shot" means either a shot was taken or a shooting foul was comitted. A "stoppage" means the clock stopped but the offensive team retained possession.',                                                   
                                                   'The euclidean distance between the points where the passer made the pass and the receiver caught the ball',
                                                   'The number of defenders who started ahead of the ball at the start of the pass and ended behind the ball when the pass was caught',
                                                   'Calculated as [3*(# of three point field goals) + 2*(# of two point field goals) + 1.5*(# of shooting fouls)] / (# of possessions). Because possessions that did not result in a shot in the first 8 seconds are included, this metric is skewed to be smaller than normal when including possessions with no shot. Only possessions with at least 1 pass are included in the calculation.']
                                    })

        st.markdown(definitions.style.hide(axis="index").to_html(), unsafe_allow_html=True)
    
    pass_df = load_data('data/transition/pass_stats.pkl')
    possessions_df = load_data('data/transition/possession_summaries.pkl')
    
    pass_df = pass_df[pass_df['Pass End'].notna()]
    
    pass_df.loc[np.isnan(pass_df['# Defenders Passed']), '# Defenders Passed'] = None
    pass_df['Pass Distance'] = round(pass_df['Pass Distance'] * 2) / 2
    pass_df.loc[pass_df['Transition Trigger'] == 'SHOT', 'Transition Trigger'] = "Made Shot"
    pass_df.loc[pass_df['Transition Trigger'] == 'REB', 'Transition Trigger'] = "Defensive Rebound"
    pass_df.loc[pass_df['Transition Trigger'] == 'TO', 'Transition Trigger'] = "Turnover"
    pass_df.loc[pass_df['Outcome'] == 'foul', 'Outcome'] = "non-shooting foul"

    pass_df = cluster_data(pass_df)
    
    show_raw_data, pass_data, selections = create_sidebar(pass_df) 
    
    pass_data_selected_team = display1(pass_data, possessions_df, selections)
    
    display2(pass_data_selected_team)
    
    show_clusters(pass_data)
    
    st.markdown('#')
    display3(pass_data, pass_df)
    
    st.markdown('#')
    st.markdown('#')
    display4(pass_data)
    
    if show_raw_data:
        st.subheader('Raw data')
        st.write(pass_data)

main()
    