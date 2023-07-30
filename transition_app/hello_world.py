import streamlit as st
import pandas as pd

df = pd.DataFrame({'first column': [1, 2, 3, 4], 'second column': [10, 20, 30, 25]})

st.write("First attempt at a table using a dataframe!")
st.write(df.style.highlight_max(axis=0))

st.write("Using st.table to display dataframep")
st.table(df)

st.line_chart(df)

x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)

option = st.selectbox('Which number do you like best?', df['first column'])

# Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone')
)

# Add a slider to the sidebar:
add_slider = st.sidebar.slider(
    'Select a range of values',
    0.0, 100.0, (25.0, 75.0)
)