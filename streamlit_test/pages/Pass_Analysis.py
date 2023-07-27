import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import sys
 
# adding Folder_2/subfolder to the system path
sys.path.append('/Users/emmaritcey/Documents/basketball_research/wisd-hackathon')
from src.visualization.draw_court import make_fig
from helpers import load_data, create_selectbox, get_num_games, add_num_games
st.set_page_config(layout="wide")
    

st.title('NBA Transition Tendencies: Passing')


def create_sidebar(df, possessions_df):

    #Selection Boxes
    series_selection, data = create_selectbox(df, 'Series', 'Series:')
    team_selection, data = create_selectbox(data, 'Team Name', 'Team:')
    game_selection, data = create_selectbox(data, 'Game Title', 'Game:')
    passer_selection, data = create_selectbox(data, 'Passer', 'Passes Made By:')
    trigger_selection, data = create_selectbox(data, 'Transition Trigger', 'Transition Initiated By:')
    outcome_selection, data = create_selectbox(data, 'Outcome', 'Transition Outcome:')

    selections = {'Series': series_selection, 'Team': team_selection, 'Game': game_selection, 'Passer': passer_selection,
                'Trigger': trigger_selection, 'Outcome': outcome_selection}

    #Check boxes
    show_passes = st.sidebar.checkbox('Show Passes')
    show_raw_data = st.sidebar.checkbox('Show Raw Data')

    #Sliders
    #minimum pass distance:
    min_pass_dist = st.sidebar.slider('Minimum Pass Distance')
    data = data[data['Pass Distance'] >= min_pass_dist]
    
    #Number Increments
    #minimum # of passes in a possession
    min_num_passes = st.sidebar.number_input('Minimum Number of Passes in the Possession', min_value=1, max_value=max(possessions_df['# Passes'].values), step=1)
    indices = possessions_df[possessions_df['# Passes']>=min_num_passes].index.values
    data = data[data['Transition Index'].isin(indices)]
    #minimum # of defenders passed on a pass
    min_def_passed = st.sidebar.number_input('Minimum # of Defenders the Ball Passed', min_value=0, max_value=5, step=1)
    data = data[data['# Defenders Passed'] >= min_def_passed]
    
    return show_passes, show_raw_data, data, min_num_passes, min_def_passed, selections


def display1(data, show_passes, selections):

    #hist_vals, bin_edges = np.histogram(df['# Defenders Passed'].values, bins=np.arange(-1,7))
    # fig = px.histogram(data, x="# Defenders Passed")
    # st.write(fig)
    st.header('Pass Locations')
    col1, col2 = st.columns([1,3])
    
    with col1:
        st.subheader('Displaying Passes for:')
        st.text('Series: ' + selections['Series'])
        st.text('Team: ' + selections['Team'])
        st.text('Game: ' + selections['Game'])
        st.text('Player: ' + selections['Passer'])
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
        if show_passes:
            for idx in data.index.values:
                try:
                    #st.write('yes')
                    x = data['Pass Start'].loc[idx][0]
                    y = data['Pass Start'].loc[idx][1]
                    dx = data['Pass End'].loc[idx][0] - x
                    dy = data['Pass End'].loc[idx][1] - y
                    if np.isnan(data['OutcomeMSG'].loc[idx]):
                        c = 'k'
                    elif data['OutcomeMSG'].loc[idx] == 1 or data['OutcomeMSG'].loc[idx] == 6:
                        c = 'r'
                    else:
                        c = 'b'
                    plt.arrow(x,y,dx,dy, head_width=1, color=c)
                except:
                    x = data['Pass Start'].loc[idx][0]
                    y = data['Pass Start'].loc[idx][1]
                    plt.plot(x,y,'ro')      
        
        st.pyplot(fig2)  
            

def display2(data):
    st.subheader('Stats For Current Selection')       
    ave_dist = round(sum(data['Pass Distance'].values)/len(data['Pass Distance']),2) 
    
    #assume each free throw opportunity ended in 1.5 points (75% free throw average estimate)
    made_shots = data[data['OutcomeMSG'] == 1]
    points3 = len(made_shots[made_shots['OutcomeMSGaction'].isin([1,79])])*3 
    points2 = len(made_shots[~made_shots['OutcomeMSGaction'].isin([1,79])])*2
    freethrows = len(data[data['OutcomeMSG']==6])*1.5
    ppp = round((points3 + points2 + freethrows) / len(data),2)
    
    num_possessions = len(data)
    num_shots = len(data[data['OutcomeMSG'].isin([1,2,79])])
    perc_shots = round(num_shots / num_possessions, 2)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric('Average Pass Distance', ave_dist)
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
    
    def_passed_means_team = data.groupby(['Team Name'])['# Defenders Passed'].mean()
    def_passed_sums_team = data.groupby(['Team Name'])['# Defenders Passed'].sum()
    num_passes_team = data.groupby(['Team Name'])['# Defenders Passed'].count()
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(x = def_passed_means_team.index, y = def_passed_means_team.values)
        fig.update_layout(width=600, height=400,  
                        title='Mean Defenders Passed on Transition Passes', title_x=0.3,
                        xaxis_title="Team") #template='plotly_dark',
        #fig.update_traces(marker=dict(size=10))
        #fig.update_yaxes(range=[min(def_passed_means_team)-0.02, max(def_passed_means_team)+0.01])
        st.plotly_chart(fig)
    
    with col2:
        num_games = get_num_games(original_data)
        num_def_passed_per_game = [def_passed_sums_team[x]/num_games[x] for x in def_passed_sums_team.index]
        
        fig = px.bar(x = def_passed_sums_team.index, y = num_def_passed_per_game)
        fig.update_layout(width=600, height=400,  
                        title='# of Defenders Passed on Transition Passes Per Game', title_x=0.2,
                        xaxis_title="Team") #template='plotly_dark',
        #fig.update_traces(marker=dict(size=10))
        #fig.update_yaxes(range=[min(def_passed_means_team)-0.02, max(def_passed_means_team)+0.01])
        st.plotly_chart(fig)
        
    
    
     

def main():
    pass_df = load_data('data/transition/pass_stats.pkl')
    possessions_df = load_data('data/transition/possession_summaries.pkl')
    
    
    pass_df.loc[np.isnan(pass_df['# Defenders Passed']), '# Defenders Passed'] = -1  
    
    show_passes, show_raw_data, pass_data, min_num_passes, min_def_passed, selections = create_sidebar(pass_df, possessions_df) 
    
    
    #pass_data = add_num_games(pass_data, num_games)
    
    display1(pass_data, show_passes, selections)
    
    display2(pass_data)
    
    st.markdown('#')
    display3(pass_data, pass_df)
    
    if show_raw_data:
        st.subheader('Raw data')
        st.write(pass_data)

main()
    


#TODO: add summarizing charts, points per possession, etc