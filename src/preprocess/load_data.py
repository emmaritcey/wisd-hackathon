import pandas as pd
import json


def load_game_file(file_path):
    '''
    load game data (either tracking or event) for a single game
    INPUT:
        - file_path, str: file path of the file being loaded
    OUTPUT:
        - df_final, df: contains all data from file
    '''
    #open file and put each line (json object) into list entry
    with open(file_path) as f:
        lines = f.read().splitlines()
        
    #create dataframe with single column for entire json object
    df_inter = pd.DataFrame(lines)
    df_inter.columns = ['json_element']
    
    #use json.loads to decode each json object into a dictionary
    #apply function applies this function to each row of the dataframe
    #use json normalize function to convert keys to be column headers and values to row elements
    df_final = pd.json_normalize(df_inter['json_element'].apply(json.loads))
    
    return df_final

def load_metadata(file_path):
    '''
    load metadata (either games, players, or teams)
    '''
    with open(file_path) as user_file:
        meta_data = json.load(user_file)
    return meta_data