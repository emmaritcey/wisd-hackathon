import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
import sys
 
# adding Folder_2/subfolder to the system path
sys.path.append('/Users/emmaritcey/Documents/basketball_research/wisd-hackathon')
from src.visualization.draw_court import make_fig
from src.utils.data_helpers import get_game_meta_data
    

st.set_page_config(layout="wide")

def main():
    st.title('NBA Transition Tendencies')
    st.markdown('#')
    st.markdown('This app is designed to assess teams transition tendencies during the 2022 ECF, WCF, and Finals using player tracking data, play-by-play data, and event data.')
    st.markdown('The 4 teams transition stats are below, gathered from nba.com/stats. Note that these stats are calculated from ALL games played throughout the 2022 playoffs while all other sections only used data from games from the 2022 ECF, WCF, and Finals.')
    st.markdown('#')
    
    trans_stats =pd.DataFrame({'Team': ['Boston Celtics', 'Dallas Mavericks', 'Golden State Warriors', 'Miami Heat'],
                               'Possessions Per Game': [15.2, 13.2, 16.6, 14.5],
                               'Points Per Possession': [1.23, 1.09, 1.11, 1.15],
                               'Points Per Game': [18.6, 14.4, 18.4, 16.7],
                               'Field Goal %': [56.9, 44.1, 56.1, 56.0],
                               'Effective Field Goal %': [63.0, 53.8, 64.4, 61.1],
                               'Free Throw Frequency': [21.2, 17.7, 12.3, 13.4],
                               'Turnover Frequency': [12.1, 7.2, 17.3, 10.7]})
    df = trans_stats.style.highlight_max(color = '#1f77b4', axis = 0, subset=trans_stats.columns[1:]).format(precision=2)

    col1, col2, _, _, _ = st.columns(5)
    with col1:
        button1 = st.button("Show Stats in Table")
    with col2:
        button2 = st.button('Show Stats in Chart')
    
    if button1:
        button2 = False
    
    if button2:
        st.markdown("To modify the chart:")
        st.markdown("- Click an active variable in the legend to hide it")
        st.markdown("- Click an unactive variable to show it")
        st.markdown("- Double click a variable in the legend to show that variable on its own")

        fig2 = px.bar(trans_stats, x='Team', y=trans_stats.columns[1:], barmode='group')#, color_discrete_sequence=color_to_plot)
        fig2.update_layout(width=1200, height=500,  
                        xaxis_title="Team", 
                        yaxis_title="",
                        legend_title=None) #template='plotly_dark',
        st.plotly_chart(fig2)
    else:
        st.markdown('The maximum value in each column is highlighted in blue')
        st.dataframe(df, hide_index=True)
    
    st.subheader("A few takeaways from these stats:")
    st.markdown("- Golden State created the most transition possessions and maintained the highest eFG% but also had the highest TO% and lowest FT%")
    st.markdown("- Boston had the highest points per possession, points per game, FG%, and FT%")
    st.markdown("- Dallas created the fewest transition possessions, and on these possessions scored the least efficiently by a large margin")
    st.markdown("#")
    st.markdown("##### The Drive Analysis and Pass Analysis pages aim to identify how teams and players are attacking in transition and when they are most successful.")
main()
