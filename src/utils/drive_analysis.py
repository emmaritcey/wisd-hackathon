import pandas as pd
import numpy as np
import math

from src.utils.data_helpers import get_player_name, travel_dist, travel_dist_1d





def get_drive_indices(possession_df, end_idx, trigger_event):
    '''
    get a list of tuples containing the start and end index for each drive/dribbling sequence in a possession
    defining a drive/dribbling sequence as one started by a touch (or start of possession) and ending with a pass or shot
    if the possession is starting off a made shot, don't look for dribbles until after first pass (inbound pass) is made
    INPUT:
        - possession_df: a single dataframe from Transition.trans_possessions (Transition.trans_possesions[idx]) - contains tracking and event info
        - end_idx, int: index of the end of the transition possession (Transition.end_of_possessions[idx])
        - trigger_event, series: event data for the event that started the transition possession (shot, TO, etc)
    OUTPUT:
        - drive_start_stops, list of tuples: for each tuple --> (start_idx, end_idx) of a drive/dribbling sequence
    '''
    
    if trigger_event['eventType'] == 'SHOT': #start search from inbound pass
        try:
            zero_idx = list(possession_df[possession_df['eventType']=='PASS'].index)[0]
        except:
            print('oh no')
        temp_df = possession_df.iloc[zero_idx:end_idx+1]
    else:
        zero_idx = 0
        temp_df = possession_df.iloc[zero_idx:end_idx+1]
    dribble_indices = list(temp_df[temp_df['eventType']=='DRIBBLE'].index) #get list of indices of each dribble
    
    dribble_start_stops = []
    for idx in dribble_indices:
        start_idx = idx
        stop_idx = idx
        while start_idx > zero_idx and possession_df['eventType'].iloc[start_idx] != 'TOUCH':
            start_idx -= 1
        while stop_idx < end_idx and possession_df['eventType'].iloc[stop_idx] != 'PASS' and possession_df['eventType'].iloc[stop_idx] != 'SHOT':
            stop_idx += 1
        dribble_start_stops.append((start_idx, stop_idx))

    drive_start_stops = list(set(dribble_start_stops))
    drive_start_stops.sort(key=lambda x: x[0]) #sort tuples in ascending order by first element
    
    return drive_start_stops
        

def time_of_drive(possession_df, start_end_indices):
    '''
    get the length of the drive, in seconds
    INPUT:
        - possession_df, df: contains tracking data of entire single possession
        - start_end_indices, list of tuples: for each tuple --> (start_idx, end_idx) of a drive/dribbling sequence
    '''

    start_idx = start_end_indices[0]
    end_idx = start_end_indices[1]
    
    start_time = possession_df['gameClock'].iloc[start_idx]
    end_time = possession_df['gameClock'].iloc[end_idx]
    
    length = round(start_time - end_time)
    time_to_drive = start_idx / 25 #seconds since possession was obtained to the start of the drive (shot clock isn't always reliable)
    
    return time_to_drive, length


def distance_dribbled_total(possession_df, start_end_indices):
    '''
    get the total distance the ball has travelled while a player is dribbling by calling travel_dist on the ball locations
    calculate the total x distance, y distance, and euclidean distance
    first need to get ball locations in suitable format (list of two lists - sublist 1 contains x locations, sublist 2 contains y locations)
    INPUT:
        - possession_df, df: contains tracking data of entire single possession
        - start_end_indices, list of tuples: for each tuple --> (start_idx, end_idx) of a drive/dribbling sequence
    OUTPUT:
        - x_dist, int: total x distance the ball travelled
        - y_dist, int: total y distance the ball travelled
        - total_dist, int: total euclidean distance the ball travelled in feet 
    '''
        
    start_idx = start_end_indices[0]
    end_idx = start_end_indices[1]
    
    ball_locations = possession_df['ball'].values[start_idx:end_idx]
    ball_x = [item[0] for item in ball_locations]
    ball_y = [item[1] for item in ball_locations]
    locations = [ball_x, ball_y]
    total_dist = travel_dist(locations)
    dist_x, dist_y = travel_dist_1d(locations)
    
    return dist_x, dist_y, total_dist
        

def distance_dribbled_discrete(possession_df, start_end_indices, shooting_side):
    '''
    x, y, and euclidean distance from start point to stop point
    INPUT:
        - possession_df: a single dataframe from Transition.trans_possessions (Transition.trans_possesions[idx]) - contains tracking and event info
        - start_end_indices, list of tuples: for each tuple --> (start_idx, end_idx) of a drive/dribbling sequence
        - shooting_side, str: 'pos' (left side) or 'neg' (right side) --> side that the offensive team is shooting on 
    '''
    
    start_idx = start_end_indices[0]
    end_idx = start_end_indices[1]
    
    start_loc = np.array(possession_df.iloc[start_idx]['ball'])
    end_loc = np.array(possession_df.iloc[end_idx]['ball'])
    
    start_loc[0]= start_loc[0]*shooting_side #flip court depending on direction
    end_loc[0] = end_loc[0]*shooting_side #flip court depending on direction
    if shooting_side == 1: #flip y axis so left to right is negative progression and right to left is positive progression
        start_loc[1] = start_loc[1]*(-1)
        end_loc[1] = end_loc[1]*(-1)
    #start_loc= start_loc*shooting_side #flip court depending on direction
    #end_loc = end_loc*shooting_side #flip court depending on direction
    
    dist_x = round(end_loc[0] - start_loc[0],2)
    dist_y = round(end_loc[1] - start_loc[1],2)
    dist = round(math.dist(start_loc[0:2], end_loc[0:2]), 2)
    
    return dist_x, dist_y, dist, start_loc, end_loc
    
    
def num_defenders_overtaken(possession_df, start_end_indices, shooting_side, team):
    '''
    INPUT:
        - possession_df: a single dataframe from Transition.trans_possessions (Transition.trans_possesions[idx]) - contains tracking and event info
        - start_end_indices, list of tuples: for each tuple --> (start_idx, end_idx) of a drive/dribbling sequence
        - shooting_side, str: 'pos' (left side) or 'neg' (right side) --> side that the offensive team is shooting on 
        - team, str: 'home' or 'away'
    '''
    
    start_idx = start_end_indices[0]
    end_idx = start_end_indices[1]
    #possession_df = possession_df.iloc[start_idx:end_idx+1]
    
    #try: 
    #get the location of the ball when ball at beginning and end of drive
    start_loc = np.array(possession_df.iloc[start_idx]['ball'])
    end_loc = np.array(possession_df.iloc[end_idx]['ball'])
    
    #if shooting_side == 'neg': #multiply everything by -1 (MAYBE CHANGE THIS LATER)
    ball_start_loc = np.array(start_loc)
    ball_end_loc = np.array(end_loc)
    ball_start_loc[0] = ball_start_loc[0]*shooting_side #flips court if shooting on negative side
    ball_end_loc[0] = ball_end_loc[0]*shooting_side #flips court if shooting of negative side
    
    #get the location of all defensive players at beginning and end of drive
    if team == 'away': #offensive team
        col = 'homePlayersLoc'
    else:
        col = 'awayPlayersLoc'
    def_locations_start = possession_df.iloc[start_idx][col]
    def_locations_end = possession_df.iloc[end_idx][col]
    
    player_x_locs_start = np.array([xyz['xyz'][0] for xyz in def_locations_start])*shooting_side #flips court if offensive team shooting on negative side
    player_x_locs_end = np.array([xyz['xyz'][0] for xyz in def_locations_end])*shooting_side #flips court if offensive team shooting on negative side
    
    ball_relative_x_start = ball_start_loc[0] - player_x_locs_start #x distance between ball and each player (pos = ball ahead, neg = ball behind)
    ball_relative_x_end = ball_end_loc[0] - player_x_locs_end

    ground_made_up = np.around(ball_relative_x_end - ball_relative_x_start, 2)
    
    #find players that the ball is behind when the pass is made (smaller x value = farther from net)
    behind_to_start = ball_start_loc[0] < np.array(player_x_locs_start)
    #find players that the ball is ahead of after the pass
    ahead_to_end = ball_end_loc[0] > np.array(player_x_locs_end)
    #count number of players the ball passed in the air
    num_def_passed = len(np.where(behind_to_start & ahead_to_end)[0])
            
    
    #except: #no catch means turnover
    #    ground_made_up = np.nan
    #    num_def_passed = np.nan
        
    return ground_made_up, num_def_passed

    
    
def get_driver(possession_df, start_end_indices, team):
    '''
    get the name of the player who is driving/dribbling the ball by  finding the player who is closest to the ball at the start and end of the drive
    INPUT:
        - possession_df: a single dataframe from Transition.trans_possessions (Transition.trans_possesions[idx]) - contains tracking and event info
        - drive_indices, tuple: start and end indices of the drive
        - team, str: 'home' or 'away'
    OUTPUT:
        - playerName, str  
    '''
    
   # start_df = possession_df.iloc[drive_indices[0]] #get tracking data at the very start of the drive

    end_df = possession_df.iloc[start_end_indices[1]] #get tracking data at the very end of the drive
    #get just the x and y coordinates of the ball
    #ball_start_loc = start_df['ball'][0:2]
    ball_end_loc = end_df['ball'][0:2]

    if team == 'home':
        col = 'homePlayersLoc'
    else:
        col = 'awayPlayersLoc'

    # #get the player who is closest to the ball at the start of the drive
    # min_dist = 100
    # for idx in range(0,5):
    #     player_loc = start_df[col][idx]['xyz'][0:2]
    #     curr_dist = math.dist(ball_start_loc, player_loc)
    #     if curr_dist < min_dist:
    #         min_dist = curr_dist
    #         min_idx = idx
    # playerId = start_df[col][min_idx]['playerId']
    # start_playerName = get_player_name(playerId)

    #get the player who is closest to the ball at the end of the drive (players can be close together at start of transition)
    min_dist = 100
    for idx in range(0,5):
        player_loc = end_df[col][idx]['xyz'][0:2]
        curr_dist = math.dist(ball_end_loc, player_loc)
        if curr_dist < min_dist:
            min_dist = curr_dist
            min_idx = idx
    playerId = end_df[col][min_idx]['playerId']
    playerName = get_player_name(playerId)
    
    return playerName


def get_possession_drives(possession_df, end_idx, shooting_side, team, event, drive_dict, trans_idx):
    '''
    get drive information and add all data into dictionary
    INPUT:
        - possession_df: a single dataframe from Transition.trans_possessions (Transition.trans_possesions[idx]) - contains tracking and event info
        - end_idx, int: index of the end of the transition possession (Transition.end_of_possessions[idx])
        - shooting_side, str: 'pos' (left side) or 'neg' (right side) --> side that the offensive team is shooting on 
        - team, str: 'home' or 'away'
        - event, series: corresponding single event information for the beginning of the transition possession
        - drive_dict, dict: contains data from all drives made in transition up until the trans_idx'th possession
        - trans_idx, int: the transition possession index (first trans poss is 0,...,end_idx)
    OUTPUT:
        - drive_dict, dict: drive_dict with drive data from the current transition possession added
    '''
    
    drive_indices = get_drive_indices(possession_df, end_idx, event)
    
    
    for idx in range(0, len(drive_indices)):
        drive_idx = drive_indices[idx]
        time_to_drive, length_of_drive_seconds = time_of_drive(possession_df, drive_idx)
        dist_x, dist_y, distance, start_loc, end_loc = distance_dribbled_discrete(possession_df, drive_idx, shooting_side)
        total_dist_x, total_dist_y, total_distance = distance_dribbled_total(possession_df, drive_idx)
        ground_made_up, num_def_passed = num_defenders_overtaken(possession_df, drive_idx, shooting_side, team)
        playerName = get_driver(possession_df, drive_idx, team)
        drive_dict['Drive Indices'].append(drive_idx)
        drive_dict['Drive Time'].append(time_to_drive)
        drive_dict['Drive Length (sec)'].append(length_of_drive_seconds)
        drive_dict['Drive Distance X'].append(dist_x)
        drive_dict['Drive Distance Y'].append(dist_y)
        drive_dict['Drive Distance'].append(distance)
        drive_dict['Drive Start'].append(start_loc)
        drive_dict['Drive End'].append(end_loc)
        drive_dict['Total Drive Distance X'].append(total_dist_x)
        drive_dict['Total Drive Distance Y'].append(total_dist_y)
        drive_dict['Total Drive Distance'].append(total_distance)
        drive_dict['Ground Made Up'].append(ground_made_up)
        drive_dict['# Defenders Passed'].append(num_def_passed)
        drive_dict['Driver'].append(playerName)
        drive_dict['Transition Index'].append(trans_idx)
        
    return drive_dict


def get_drive_data(trans_possessions, end_indices, events_df, shooting_directions, team, trans_idx):
    '''
    get information on all passes from all transition possessions
    INPUT:
        - trans_possessions, list of df's: stores df for each transition possession (Transition.trans_possesions)
        - end_indices, list of ints: indices of the end of each transition possession (where the shot, TO, foul, stoppage, etc occurred)
        - events_df, df: dataframe containing event info for each transition opportunity
        - shooting_directions, 2d tuple: contains 1 (right side) or -1 (left side) first # is direction in first half, second is direction in second half
        - team, str: 'home' or 'away'    
        - trans_idx, int: represents the ith transition possession out of all the data
    OUTPUT:
        - drive_dict, dict: contains data from all passes made in transition (all possessions)

    '''
    
    #pass index --> index of the pass within that possession's tracking df
    #pass time--> seconds elapsed since change of possession event occurred until the pass
    #ground made up --> ground the ball made up on each defender from the pass (if 2 feet behind defender and then 1 foot behind defender after pass, then it would be 1 for that defender)
    #defenders passed --> number of defenders the ball passed in the air
    #transition index --> the transition possession the pass occurred in (to be able to map it back to its tracking and event data)
    drive_dict = {'Drive Indices': [], 'Drive Time': [], 'Drive Length (sec)': [], 'Drive Distance X': [], 'Drive Distance Y': [], 
                  'Drive Distance': [], 'Drive Start': [], 'Drive End': [], 'Drive Distance': [], 'Total Drive Distance X': [], 
                  'Total Drive Distance Y': [], 'Total Drive Distance': [], 'Ground Made Up': [], '# Defenders Passed': [], 
                  'Driver': [], 'Transition Index': []}
    
    for idx in range(0, len(trans_possessions)):
        event = events_df.iloc[idx]
        if event['PERIOD'] == 1 or event['PERIOD'] == 2:
            shooting_direction = shooting_directions[0]
        else:
            shooting_direction = shooting_directions[1]
            
        pass_dict = get_possession_drives(trans_possessions[idx], end_indices[idx], shooting_direction, team, events_df.iloc[idx], drive_dict, trans_idx+idx)
        
        
    pass_df = pd.DataFrame(pass_dict)
    return pass_df, trans_idx+len(trans_possessions)
    

