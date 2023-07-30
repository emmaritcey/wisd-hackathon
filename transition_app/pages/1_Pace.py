import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

import sys
import plotly.graph_objects as go
from plotly.subplots import make_subplots
 
# adding Folder_2/subfolder to the system path
sys.path.append('/Users/emmaritcey/Documents/basketball_research/wisd-hackathon')
from src.visualization.draw_court import make_fig
from helpers import load_data, create_selectbox, get_num_games, get_ppp, get_ppp_df, get_num_games_player, get_ppp_player_df, improve_text_position
st.set_page_config(layout="wide")


def main():
    st.title('Pace of Play')
    st.markdown('''For the purpose of this project, a transition possession was defined as the first 8 seconds of a possession after a 
             team has gained possession after forcing a turnover, gathering a defensive rebound, or inbounding the ball after being 
             scored on. A possession in which a team did not take a shot in the first 8 seconds is still considered a transition 
             possession, but with the outcome being 'no shot'.''')
    st.markdown('''Below  are two statistics that help gain an initial sense of a team's pace of play and how often they play
             in transition (ie take a shot in the first 8 seconds of a possession). There are of course situational factors that play 
             into whether a team will seek an early shot, including time and score, personell, and game flow.''')
    
    df = load_data('data/transition/possession_summaries.pkl')
    df.loc[df['Outcome'] == 'foul', 'Outcome'] = "non-shooting foul"

    time_crossed_mean = df.groupby(['Team Name'])['Time Ball Crosses Half'].mean()
    time_crossed_median = df.groupby(['Team Name'])['Time Ball Crosses Half'].median()
        
    col1, col2, col3 = st.columns([15,70,15])
    with col2:
        fig = px.bar(x = time_crossed_mean.index, y = time_crossed_mean.values)
        #fig = px.bar(x = time_crossed_mean.index, y = [time_crossed_mean.values,time_crossed_median.values], barmode='group')
        fig.update_layout(width=600, height=400,  
                        title=dict(text='Average Time the Ball Crosses Half', x=0.25, font=dict(size=23)),
                        xaxis_title="Team",
                        yaxis_title="Seconds") #template='plotly_dark',
        st.plotly_chart(fig)
    
    st.markdown("#")
    
    boston = df[df['Team Name']=='Boston Celtics']
    dallas = df[df['Team Name']=='Dallas Mavericks']
    goldenstate = df[df['Team Name']=='Golden State Warriors']
    miami = df[df['Team Name']=='Miami Heat']
    colors = px.colors.qualitative.Plotly

    fig3 = make_subplots(rows=2, cols=2, 
                        subplot_titles=("Boston Celtics", "Dallas Maverics", "Golden State Warriors", 'Miami Heat'),
                        specs=[[{"type": "domain"}, {"type": "domain"}],[{"type": "domain"}, {"type": "domain"}]],
                        horizontal_spacing=0.001,
                        vertical_spacing=0.1)

    fig3.add_trace(go.Pie(values=boston['Outcome'].value_counts(),
                        labels=boston['Outcome'].value_counts().index,
                        marker_colors=colors),
                row=1, col=1)

    fig3.add_trace(go.Pie(values=dallas['Outcome'].value_counts(),
                        labels=dallas['Outcome'].value_counts().index),
                row=1, col=2)

    fig3.add_trace(go.Pie(values=goldenstate['Outcome'].value_counts(),
                        labels=goldenstate['Outcome'].value_counts().index),
                row=2, col=1)

    fig3.add_trace(go.Pie(values=miami['Outcome'].value_counts(),
                        labels=miami['Outcome'].value_counts().index),
                row=2, col=2)
    fig3.update_layout(height=900, 
                       width=1200, 
                       title=dict(text='Transition Possession Outcomes', x=0.28, font=dict(size=25))
    )

    st.plotly_chart(fig3)


    
main()
    
    
