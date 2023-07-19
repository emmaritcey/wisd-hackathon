import numpy as np
import math
from src.utils.data_helpers import get_player_name



def get_pass_indices(possession_df, end_idx):
    '''
    get the indices of each pass from a single possession
    INPUT:
        - possession_df: a single dataframe from Transition.trans_possessions (Transition.trans_possesions[idx]) - contains tracking and event info
        - end_idx, int: index of the end of the transition possession (Transition.end_of_possessions[idx])
    OUTPUT:
        - pass_indices, list
    '''

    possession_df = possession_df.iloc[0:end_idx]
    pass_indices = list(possession_df[possession_df['eventType']=='PASS'].index)  #get list of indices of each pass
    
    return pass_indices


def num_defenders_overtaken(possession_df, pass_idx, end_idx, shooting_side, team):
    '''
    INPUT:
        - possession_df: a single dataframe from Transition.trans_possessions (Transition.trans_possesions[idx]) - contains tracking and event info
        - pass_idx, int: index of the pass
        - end_idx, int: index of the end of the transition possession (Transition.end_of_possessions[idx])
        - shooting_side, str: 'pos' (left side) or 'neg' (right side) --> side that the offensive team is shooting on 
        - team, str: 'home' or 'away'
    '''
    possession_df = possession_df.iloc[pass_idx:end_idx]
    
    try: 
        #say first touch after the pass is when it's caught
        #get the location of the ball when ball is thrown and caught
        catch_idx = np.where(possession_df['eventType'].values == 'TOUCH')[0][0]
        ball_start_loc = possession_df.iloc[0]['ball']
        ball_end_loc = possession_df.iloc[catch_idx]['ball']
        
        if shooting_side == 'neg': #multiply everything by -1 (MAYBE CHANGE THIS LATER)
            ball_start_loc = -1*ball_start_loc
            ball_end_loc = -1*ball_end_loc
        
        #get the location of all defensive players when ball is thrown and when ball is caught
        if team == 'away': #offensive team
            col = 'homePlayersLoc'
        else:
            col = 'awayPlayersLoc'
        def_locations_start = possession_df.iloc[0][col]
        def_locations_end = possession_df.iloc[catch_idx][col]
        
        player_x_locs_start = [xyz['xyz'][0] for xyz in def_locations_start]
        player_x_locs_end = [xyz['xyz'][0] for xyz in def_locations_end]
        
        ball_relative_x_start = np.array(ball_start_loc[0]) - np.array(player_x_locs_start) #x distance between ball and each player (pos = ball ahead, neg = ball behind)
        ball_relative_x_end = np.array(ball_end_loc[0]) - np.array(player_x_locs_end)

        ground_made_up = ball_relative_x_end - ball_relative_x_start
        
        #find players that the ball is behind when the pass is made (smaller x value = farther from net)
        behind_to_start = ball_start_loc[0] < np.array(player_x_locs_start)
        #find players that the ball is ahead of after the pass
        ahead_to_end = ball_end_loc[0] > np.array(player_x_locs_end)
        #count number of players the ball passed in the air
        num_def_passed = len(np.where(behind_to_start & ahead_to_end)[0])
                
    
    except: #no catch means turnover
        ground_made_up = np.nan
        num_def_passed = np.nan
        
    return ground_made_up, num_def_passed
    
    
def time_of_passes(pass_indices):
    '''
    get the time, in seconds, since the change in possession occurred that each pass was made
    INPUT:
        - pass_indices, list: indices of each pass made in a possession
    OUTPUT:
        - times, list: times in seconds since the change in possession that each pass was made
    '''
    times = []
    for idx in pass_indices:
        #get seconds since possession was obtained (shot clock isn't always reliable)
        times.append(idx / 25)

    return times
    
    
def get_passer(possession_df, pass_idx):
    '''
    get the name of the player who made the pass
    INPUT:
        - possession_df: a single dataframe from Transition.trans_possessions (Transition.trans_possesions[idx]) - contains tracking and event info
        - pass_idx, int: index of the pass  
    OUTPUT:
        - playerName, str  
    '''
    
    pass_df = possession_df.iloc[pass_idx]
    #get just the x and y coordinates of the ball
    ball_loc = pass_df['ball'][0:2]

    #get the player who made the pass
    #consider them to be the player closest to the ball at the time of the pass 
    min_dist = 100
    for idx in range(0,5):
        player_loc = pass_df['awayPlayersLoc'][idx]['xyz'][0:2]
        curr_dist = math.dist(ball_loc, player_loc)
        if curr_dist < min_dist:
            min_dist = curr_dist
            min_idx = idx


    try:
        playerId = pass_df['awayPlayersLoc'][min_idx]['playerId']
    except AttributeError:
        print('oh no')
    playerName = get_player_name(playerId)
    
    
    return playerName
    
    
    
def get_possession_passes(possession_df, end_idx, shooting_side, team, event, pass_dict, trans_idx):
    '''
    get pass information and add all data into dictionary
    INPUT:
        - possession_df: a single dataframe from Transition.trans_possessions (Transition.trans_possesions[idx]) - contains tracking and event info
        - end_idx, int: index of the end of the transition possession (Transition.end_of_possessions[idx])
        - shooting_side, str: 'pos' (left side) or 'neg' (right side) --> side that the offensive team is shooting on 
        - team, str: 'home' or 'away'
        - event, series: corresponding single event information for the beginning of the transition possession
        - pass_dict, dict: contains data from all passes made in transition up until the trans_idx'th possession
        - trans_idx, int: the transition possession index (first trans poss is 0,...,end_idx)
    OUTPUT:
        - pass_dict, dict: pass_dict with pass data from the current transition possession added
    '''
    pass_indices = get_pass_indices(possession_df, end_idx)
    time_to_pass = time_of_passes(pass_indices)
    
    
    for idx in range(0, len(pass_indices)):
        pass_idx = pass_indices[idx]
        time = time_to_pass[idx]
        ground_made_up, num_def_passed = num_defenders_overtaken(possession_df, pass_idx, end_idx, shooting_side, team)
        playerName = get_passer(possession_df, pass_idx)
        pass_dict['Pass Index'].append(pass_idx)
        pass_dict['Pass Time'].append(time)
        pass_dict['Ground Made Up'].append(ground_made_up)
        pass_dict['# Defenders Passed'].append(num_def_passed)
        pass_dict['Passer'].append(playerName)
        pass_dict['Transition Index'].append(trans_idx)
        
    return pass_dict


def get_all_passes(trans_possessions, end_indices, events_df, shooting_side, team):
    '''
    get information on all passes from all transition possessions
    INPUT:
        - trans_possessions, list of df's: stores df for each transition possession (Transition.trans_possesions)
        - end_indices, list of ints: indices of the end of each transition possession (where the shot, TO, foul, stoppage, etc occurred)
        - events_df, df: dataframe containing event info for each transition opportunity
        - shooting_side, str: 'pos' (left side) or 'neg' (right side) --> side that the offensive team is shooting on 
        - team, str: 'home' or 'away'    
    OUTPUT:
        - pass_dict, dict: contains data from all passes made in transition (all possessions)

    '''
    
    #pass index --> index of the pass within that possession's tracking df
    #pass time--> seconds elapsed since change of possession event occurred until the pass
    #ground made up --> ground the ball made up on each defender from the pass (if 2 feet behind defender and then 1 foot behind defender after pass, then it would be 1 for that defender)
    #defenders passed --> number of defenders the ball passed in the air
    #transition index --> the transition possession the pass occurred in (to be able to map it back to its tracking and event data)
    pass_dict = {'Pass Index': [], 'Pass Time': [], 'Ground Made Up': [], '# Defenders Passed': [], 'Passer': [], 'Transition Index': []}
    
    for idx in range(0, len(trans_possessions)):
        pass_dict = get_possession_passes(trans_possessions[idx], end_indices[idx], shooting_side, team, events_df.iloc[idx], pass_dict, idx)
        
    return pass_dict
    