import pandas as pd
import json


def load_file(test_file):
    #open file and put each line (json object) into list entry
    with open(test_file) as f:
        lines = f.read().splitlines()
        
    #create dataframe with single column for entire json object
    df_inter = pd.DataFrame(lines)
    df_inter.columns = ['json_element']
    
    #use json.loads to decode each json object into a dictionary
    #apply function applies this function to each row of the dataframe
    #use json normalize function to convert keys to be column headers and values to row elements
    df_final = pd.json_normalize(df_inter['json_element'].apply(json.loads))
    
    return df_final