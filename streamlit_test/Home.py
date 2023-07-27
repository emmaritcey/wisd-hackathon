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
    


def main():
    st.title('NBA Transition Tendencies')
    
    
main()
