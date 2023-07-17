import numpy as np

def get_possession_length(possession_df, end_idx):
    '''
    get elapsed time between turnover and shot
    INPUT:
        - possession_df, df: contains tracking data of entire single possession
        - end_idx, str: index of the end of the possession (shot, stoppage, TO, etc)
    OUTPUT:
        - poss_length, int: length of possession in seconds
    '''
    start_time = possession_df.iloc[0]['gameClock']
    end_time = possession_df.iloc[end_idx]['gameClock']
    poss_length = round(start_time - end_time,2)
    
    return poss_length



def count_event(possession_df, event_name, end_idx, poss_length):
    '''
    count number of dribbles or passes between turnover and shot/end of possession
    INPUT:
        - possession_df, df: contains tracking data of entire single possession
        - event_name, str: 'PASS' or 'DRIBBLE'
        - end_idx, str: index of the end of the possession (shot, stoppage, TO, etc)
        - poss_length: length of possession in seconds (get from get_possession_length)
    OUTPUT:
        n_events: number of dribbles or passes
        n_events_per_sec: number of dribbles or passes per second
    '''
    possession_df = possession_df.iloc[0:end_idx]
    n_events = len(np.where(possession_df['eventType'].values == event_name)[0])
    n_events_per_sec = round(n_events / poss_length, 2)
    
    return n_events, n_events_per_sec


def pass_length(possession_df, pass_idx):
    '''
    get the x distance (up the court) and y distance (across the court) of a single pass
    INPUT:
        - possession_df, df: contains tracking data of entire single possession
        - pass_idx, int: index of the pass to calculate the distance of
    OUTPUT:
        - dist_x, int: x distance (up the court)
        - dist_y, int: y distance (across the court)
    '''
    possession_df = possession_df.iloc[pass_idx:]
    try:
        catch_idx = np.where(possession_df['eventType'].values == 'TOUCH')[0][0]
        ball_start_loc = possession_df.iloc[0]['ball']
        ball_end_loc = possession_df.iloc[catch_idx]['ball']
        
        dist_x = round(ball_start_loc[0] - ball_end_loc[0],2)
        dist_y = round(ball_start_loc[1] - ball_end_loc[1],2)
    except: #no catch means turnover
        dist_x = np.nan
        dist_y = np.nan

    
    return dist_x, dist_y


def travel_dist(locations):
    '''
    calculate the total distance the object has travelled by calculating each consecutive euclidean distance
    INPUT:
        - locations, list containing 2 lists: sublist 1 contains x locations, sublist 2 contains y locations
    OUTPUT:
        - total distance the ball has travelled in a possession
    '''
    # get the differences of each consecutive value in each sublist
    diff = np.diff(locations, axis=1)
    # square the differences and add corresponding x and y pairs, then get the square root of that sum
    dist = np.sqrt((diff ** 2).sum(axis=0))
    # Then return the sum of all the distances
    return round(dist.sum(), 2)


def get_ball_distances(possession_df, end_idx):
    '''
    get the total distance the ball has travelled by calling travel_dist on the ball locations
    first need to get ball locations in suitable format (list of two lists - sublist 1 contains x locations, sublist 2 contains y locations)
    INPUT:
        - possession_df, df: contains tracking data of entire single possession
        - end_idx, str: index of the end of the possession (shot, stoppage, TO, etc)   
    OUTPUT:
        - ball_dist, int: total distance the ball travelled in feet 
    '''
    ball_locations = possession_df['ball'].values[0:end_idx]
    ball_x = [item[0] for item in ball_locations]
    ball_y = [item[1] for item in ball_locations]
    locations = [ball_x, ball_y]
    ball_dist = travel_dist(locations)
    
    return ball_dist


def average_speed(distance, possession_length):
    '''
    get the average speed in miles per hour of an object in a single possession
    INPUT:
        - distance, int: distance covered during possession in feet
        - possession_length, int: length of possession in seconds
    OUTPUT:
        - speed in mph
    '''
    fps = distance / possession_length #feet/second
    return round(fps * 0.681818, 2) #miles per hour



def get_player_distance(player_locs, player_num):
    '''
    get the distance travelled by a single player throughout a possession
    INPUT:
        - player_locs: pandas series: 'homePlayersLoc' or 'awayPlayersLoc' column from possession dataframe
        - player_num, int: player on the court, 0, 1, 2, 3, or 4
    OUTPUT:
        - dist, int: distance travelled by the player throughout a possession
        - playerId, str: player's playerId
    '''
    
    #get player's playerId to ensure we're always getting the same player's location
    playerId = player_locs.iloc[0][player_num]['playerId']
    
    #list of dictionaries containing a single player's info from 'homePlayersLoc' or 'awayPlayersLoc'
    player_dcts = [dct for lst in player_locs.values for dct in lst if dct['playerId'] == playerId]
    
    #get list of lists containing a player's x,y,z coordinate info
    coordinates = [d['xyz'] for d in player_dcts]
    
    #get player's x and y locations
    loc_x = [item[0] for item in coordinates]
    loc_y = [item[1] for item in coordinates]
    
    locations = [loc_x, loc_y]
    dist = travel_dist(locations)
    
    return dist, playerId



def get_poss_summary(possession_df, end_idx, team):
    '''
    Get summary of a single transition possession: 
        - length of possession in seconds
        - # of dribbles and # of passes, total and per second
        - length of each pass
        - distance and speed of ball and each player
        
    possession_df: a single dataframe from Transition.trans_possessions (Transition.trans_possesions[idx])
    end_idx, int: index of the end of the transition possession (Transition.end_of_possessions[idx])
    team, str: 'home' or 'away'
    
    '''
    #get length of possession in seconds
    poss_length = get_possession_length(possession_df, end_idx)
    #get number of dribbles
    num_dribbles, num_dribbles_per_sec = count_event(possession_df, 'DRIBBLE', end_idx, poss_length)
    #get number of passes
    num_passes, num_passes_per_sec = count_event(possession_df, 'PASS', end_idx, poss_length)
    #get the length of each pass
    pass_lengths = []
    passes = np.where(possession_df['eventType'].values == 'PASS')[0]
    if len(passes) > 0:
        for i in range(0,num_passes):
            pass_idx = passes[i]
            pass_lengths.append(pass_length(possession_df, pass_idx))
    
    #get the total distance travelled by the ball and its average speed
    
    ball_dist = get_ball_distances(possession_df, end_idx)
    avg_speed_ball = average_speed(ball_dist, poss_length)
    
    #get the total distance travelled by each offensive and defensive player and their average speed
    if team == 'home':
        off_col = 'homePlayersLoc'
        def_col = 'awayPlayersLoc'
    else:
        off_col = 'awayPlayersLoc'
        def_col = 'homePlayersLoc'
    off_player_locs = possession_df[off_col][0:end_idx]
    def_player_locs = possession_df[def_col][0:end_idx]
    off_distances = {}
    off_speeds = {}
    def_distances = {}
    def_speeds = {}
    for i in range(0,5):
        off_player_dist, playerId = get_player_distance(off_player_locs, i)
        off_distances[playerId] = off_player_dist
        off_speeds[playerId] = average_speed(off_player_dist, poss_length)
        def_player_dist, def_playerId = get_player_distance(def_player_locs, i)
        def_distances[def_playerId] = def_player_dist
        def_speeds[def_playerId] = average_speed(def_player_dist, poss_length)
    
    summary_dict = {'Possession Length': poss_length, '# Dribbles': num_dribbles, '# Passes': num_passes, 'Pass Lengths': pass_length, 
                    'Ball Distance': ball_dist, 'Average Ball Speed': avg_speed_ball, 'Off Player Distances': off_player_dist, 
                    'Off Player Speeds': off_speeds, 'Def Player Distances': def_player_dist, 'Def Player Speeds': def_speeds}
    
    return summary_dict


def get_all_poss_summaries(trans_possessions, end_indices, team):
    '''
    create a list of dictionaries containing the summaries of each transition possession
    INPUT:
        - trans_possessions, list of df's: stores df for each transition possession (Transition.trans_possesions)
        - end_indices, list of ints: indices of the end of each transition possession (where the shot, TO, foul, stoppage, etc occurred)
        - team, str: 'home' or 'away'
    OUTPUT:
        - trans_summaries, list of dicts: contains a dictionary for each transition possession which summarizes the possession
    '''
    
    trans_summaries = []
    #iterate through list of dataframes
    for i in range(0, len(trans_possessions)):
        #print(trans_possessions[i])
        trans_summaries.append(get_poss_summary(trans_possessions[i], end_indices[i], team))
        
    return trans_summaries
    