import pandas as pd
import numpy as np
import os
import pickle
from src.utils.pass_analysis import get_pass_data
from src.utils.data_helpers import get_team_name, travel_dist, get_game_title
from src.utils.drive_analysis import get_drive_data

from Transition import Transition



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

def time_ball_crossed_half(possession_df, end_idx, shooting_side):
    '''
    get the time it takes for the ball to cross half court
    INPUT:
        - possession_df, df: contains tracking data of entire single possession
        - end_idx, str: index of the end of the possession (shot, stoppage, TO, etc)
        - shooting_side, int: 1 (left side) or -1 (right side) --> side that the offensive team is shooting on 
    OUTPUT:
        - elapsed, int: -1 if ball never crossed half
    '''
    possession_df = possession_df.iloc[0:end_idx+1]
    if possession_df['PERIOD'].iloc[0] <= 2:
        shooting_side = shooting_side[0]
    else:
        shooting_side = shooting_side[1]
    try:
        ball_locs = possession_df['ball'].values
        x_locs = np.array([x[0] for x in ball_locs])*shooting_side
        idx = np.where(x_locs>=0)[0][0]

        start_time = possession_df['gameClock'].iloc[0]
        end_time = possession_df['gameClock'].iloc[idx]

        elapsed = round(start_time - end_time,2)
    except:
        elapsed = -1
        
    return elapsed
    


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
    possession_df = possession_df.iloc[0:end_idx+1]
    n_events = len(np.where(possession_df['eventType'].values == event_name)[0])
    n_events_per_sec = round(n_events / poss_length, 2)
    
    return n_events, n_events_per_sec


def count_drives(possession_df, end_idx, trigger_event):
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

    num_drives = len(list(set(dribble_start_stops)))
 
    return num_drives




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
    ball_locations = possession_df['ball'].values[0:end_idx+1]
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


def get_player_locations(possession_df, end_idx, team):
    
    frame_num = 12 #to get approx 0.5 seconds into possessioin, use the 12th frame

    if end_idx >= frame_num:
        frame = possession_df.iloc[frame_num]
        if team == 'home':
            off_loc_str = 'homePlayersLoc'
            def_loc_str = 'awayPlayersLoc'
        else:
            off_loc_str = 'awayPlayersLoc'
            def_loc_str = 'homePlayersLoc'
        
        off_locs = frame[off_loc_str]

        def_locs = frame[def_loc_str]
        
        ball_locs = frame['ball']
    else:
        off_locs = None
        def_locs = None
        ball_locs = None
        
    return off_locs, def_locs, ball_locs
          
        
    
def get_poss_summary(possession_df, end_idx, event, team, shooting_sides):
    '''
    Get summary of a single transition possession: 
        - length of possession in seconds
        - # of dribbles and # of passes, total and per second
        - length of each pass
        - distance and speed of ball and each player
        
    INPUT:
        - possession_df: a single dataframe from Transition.trans_possessions (Transition.trans_possesions[idx])
        - end_idx, int: index of the end of the transition possession (Transition.end_of_possessions[idx])
        - event, series: corresponding single event information for the beginning of the transition possession
        - team, str: 'home' or 'away'
        - shooting_side, int: 1 (left side) or -1 (right side) --> side that the offensive team is shooting on 
        - shooting_side, int: -1 or 1
    OUTPUT:
        - summary_dict, dict: dictionary containing summary of a single transition possession
    
    '''
    #get length of possession in seconds
    poss_length = get_possession_length(possession_df, end_idx)
    #get number of dribbles
    num_dribbles, num_dribbles_per_sec = count_event(possession_df, 'DRIBBLE', end_idx, poss_length)
    #get number of passes
    num_passes, num_passes_per_sec = count_event(possession_df, 'PASS', end_idx, poss_length)
    #get number of drives
    num_drives = count_drives(possession_df, end_idx, event)
    #get time taken for ball to cross half
    time_to_half = time_ball_crossed_half(possession_df, end_idx, shooting_sides)
    #get offensive and defensive locations 0.5 seconds into transition possession
    period = possession_df['PERIOD'].iloc[0]
    if period <= 2:
        shooting_side = shooting_sides[0]
    else:
        shooting_side = shooting_sides[1]
    off_start_locs, def_start_locs, ball_start_loc = get_player_locations(possession_df, end_idx, team)
    
    
    
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
    
    trigger = event['eventType']
    outcome = event['OUTCOME']
    outcome_eventmsg = event['OUTCOME MSGTYPE']
    outcome_eventmsgaction = event['OUTCOME MSGACTIONTYPE']
    #'Pass Lengths': pass_lengths, 
    summary_dict = {'Period': period, 'Shooting Side': shooting_side, 'Possession Length': poss_length, 'Time Ball Crosses Half': time_to_half, '# Dribbles': num_dribbles, 
                    '# Drives': num_drives, '# Passes': num_passes, 'Ball Distance': ball_dist, 'Average Ball Speed': avg_speed_ball, 
                    'Off Start Locs': off_start_locs, 'Def Start Locs': def_start_locs, 'Ball Start Loc': ball_start_loc, 'Off Player Distances': off_distances, 
                    'Off Player Speeds': off_speeds, 'Def Player Distances': def_distances, 'Def Player Speeds': def_speeds,
                    'Trigger': trigger, 'Outcome': outcome, 'OutcomeMSG': outcome_eventmsg, 'OutcomeMSGaction': outcome_eventmsgaction}
    
    return summary_dict


def get_all_poss_summaries(trans_possessions, end_indices, events_df, team, shooting_directions, first_x_seconds = 8):
    '''
    create a list of dictionaries containing the summaries of each transition possession
    INPUT:
        - trans_possessions, list of df's: stores df for each transition possession (Transition.trans_possesions)
        - end_indices, list of ints: indices of the end of each transition possession (where the shot, TO, foul, stoppage, etc occurred)
        - events_df, df: dataframe containing event info for each transition opportunity
        - team, str: 'home' or 'away'
        - shooting_side, int: 1 (left side) or -1 (right side) --> side that the offensive team is shooting on 
        - first_x_seconds, int, optional: only gather info for first x seconds of transition possession (likely use to look at first 3 seconds)
    OUTPUT:
        - trans_summaries, list of dicts: contains a dictionary for each transition possession which summarizes the possession
    '''
    
    trans_summaries = []
    #iterate through list of dataframes
    for i in range(0, len(trans_possessions)):
        end_indice = end_indices[i]
        #print(trans_possessions[i])
        if first_x_seconds == 8: #use end_indices[i] as the final frame of the possession
            trans_summaries.append(get_poss_summary(trans_possessions[i], end_indice, events_df.iloc[i], team, shooting_directions))
        else: #looking at shorter range of time, say first three seconds of the possession
            time_end_indice = first_x_seconds*25 + 1 #25 frames per second
            if time_end_indice > end_indice: #transition possession ended before the chosen time
                trans_summaries.append(get_poss_summary(trans_possessions[i], end_indice, events_df.iloc[i], team, shooting_directions))
            else: 
                trans_summaries.append(get_poss_summary(trans_possessions[i], time_end_indice, events_df.iloc[i], team, shooting_directions))
        
    return trans_summaries
    

def get_poss_outcomes(all_poss_summaries, type):
    '''
    from the pass summary data, record the trigger/outcome for each pass to add to the pass analysis dataframe
    INPUT:
        - all_poss_summaries, dict: dict containing the summaries of each transition possession, created from get_all_poss_summaries()
    '''
    triggers = []
    outcomes = []
    outcomes_msg = []
    outcomes_msgaction = []
    
    if type == 'pass':
        col = '# Passes'
    else:
        col = '# Drives'
  

    for idx in range (0,len(all_poss_summaries)):
        num = all_poss_summaries[idx][col]
        for jdx in range(0,num):
            triggers.append(all_poss_summaries[idx]['Trigger'])
            outcomes.append(all_poss_summaries[idx]['Outcome'])
            outcomes_msg.append(all_poss_summaries[idx]['OutcomeMSG'])
            outcomes_msgaction.append(all_poss_summaries[idx]['OutcomeMSGaction'])
    
    return triggers, outcomes, outcomes_msg, outcomes_msgaction
            

    
def get_single_game_data(trans_object, team, trans_idx, first_x_seconds = 8, all_possessions = True):
    '''
    transition stats for a single team from a single game
    INPUT:
        - trans_possessions, list of df's: stores df for each transition possession (Transition.trans_possesions)
        - end_indices, list of ints: indices of the end of each transition possession (where the shot, TO, foul, stoppage, etc occurred)
        - events_df, df: dataframe containing event info for each transition opportunity
        - team, str: 'home' or 'away'
        - first_x_seconds, int, optional: only gather info for first x seconds of transition possession (likely use to look at first 3 seconds)
        - all_possessions, boolean, default = True: get transition data for ALL transition possessions in the game
    '''
    possessions_tracking = trans_object.trans_possessions
    end_of_possessions = trans_object.end_of_possessions
    possessions_event = trans_object.event_trans_opp
    
    if team == 'home':
        shooting_directions = trans_object.meta_data['homeDirection']
        teamId = trans_object.meta_data['homeTeamId']
        points_scored = trans_object.meta_data['homeScore']
        game_won = trans_object.meta_data['homeWin']
        #teamName = trans_object.meta_data['homeTeamName']
        #teamId = get_team_id(teamName)
    else:
        shooting_directions = trans_object.meta_data['awayDirection']
 
        teamId = trans_object.meta_data['awayTeamId']
        points_scored = trans_object.meta_data['awayScore']
        game_won = trans_object.meta_data['awayWin']
        #teamName = trans_object.meta_data['awayTeamName']
        #teamId = get_team_id(teamName)
    gameId = trans_object.meta_data['id']
    nba_gameId = trans_object.meta_data['nbaId']
    series = trans_object.meta_data['series']
    
  
    trans_summaries = get_all_poss_summaries(possessions_tracking, end_of_possessions, possessions_event, team, shooting_directions, first_x_seconds) 
    pass_df = get_pass_data(possessions_tracking, end_of_possessions, possessions_event, shooting_directions, team, trans_idx)
    drive_df, trans_idx = get_drive_data(possessions_tracking, end_of_possessions, possessions_event, shooting_directions, team, trans_idx)
    
    #add the triggers/outcomes to each pass in pass_df
    triggers, outcomes, outcomes_msg, outcomes_msgaction = get_poss_outcomes(trans_summaries, 'pass')
    pass_df['Transition Trigger'] = triggers
    pass_df['Outcome'] = outcomes
    pass_df['OutcomeMSG'] = outcomes_msg
    pass_df['OutcomeMSGaction'] = outcomes_msgaction
    
    #add the triggers/outcomes to each drive in drive_df
    triggers, outcomes, outcomes_msg, outcomes_msgaction = get_poss_outcomes(trans_summaries, 'drive')
    drive_df['Transition Trigger'] = triggers
    drive_df['Outcome'] = outcomes
    drive_df['OutcomeMSG'] = outcomes_msg
    drive_df['OutcomeMSGaction'] = outcomes_msgaction
    
    #add the triggers/outcomes to each drive in drive_df
    #merge with pass_df on transition index to get data since trans_summaries counts # of dribbles, not # of drives
    #temp = pass_df[['Transition Index', 'Transition Trigger', 'Outcome', 'OutcomeMSG', 'OutcomeMSGaction']].drop_duplicates(ignore_index=True)
    #drive_df = drive_df.merge(temp, left_on=['Transition Index'], right_on=['Transition Index'], how='left')
        
    #convert dictionary to dataframe 
    trans_summaries_df = pd.DataFrame(trans_summaries)
    
    game_title = get_game_title(nba_gameId)
    #add team and game info to both dataframes
    trans_summaries_df['Team Id'] = teamId
    trans_summaries_df['Team Name'] = get_team_name(teamId)
    trans_summaries_df['NBA Game Id'] = nba_gameId
    trans_summaries_df['Game Id'] = gameId
    trans_summaries_df['Game Title'] = game_title
    trans_summaries_df['Series'] = series
    trans_summaries_df['Points Scored'] = points_scored
    trans_summaries_df['Win'] = game_won
    pass_df['Team Id'] = teamId
    pass_df['Team Name'] = get_team_name(teamId)
    pass_df['NBA Game Id'] = nba_gameId
    pass_df['Game Id'] = gameId
    pass_df['Game Title'] = game_title
    pass_df['Series'] = series
    pass_df['Points Scored'] = points_scored
    pass_df['Win'] = game_won
    drive_df['Team Id'] = teamId
    drive_df['Team Name'] = get_team_name(teamId)
    drive_df['NBA Game Id'] = nba_gameId
    drive_df['Game Id'] = gameId
    drive_df['Game Title'] = game_title
    drive_df['Series'] = series
    drive_df['Points Scored'] = points_scored
    drive_df['Win'] = game_won
    
    
    return trans_summaries_df, pass_df, drive_df, trans_idx


def get_all_games_data():
    
    #save the data
    save_loc = 'data/transition_test/'
    if os.path.isdir(save_loc) == False:
        os.mkdir(save_loc)
    if os.path.isdir(save_loc+'possessions_tracking_data/') == False:
        os.mkdir(save_loc+'possessions_tracking_data/')
    
    
    
    #transition_objects = []
    #gameId_list = []
    #team_list = []
    all_poss_summaries = pd.DataFrame()
    all_pass_stats = pd.DataFrame()
    all_drive_stats = pd.DataFrame()
    trans_idx = 0
    print('Getting transition data for game:')
    for gameId in os.listdir('data/games'):
        print(gameId)
        for team in ['home', 'away']:
            transition = Transition(gameId, team)
            if team == 'home':
                teamName = transition.meta_data['homeTeamName']
            else:
                teamName = transition.meta_data['awayTeamName']
            possession_summaries, pass_stats, drive_stats, trans_idx = get_single_game_data(transition, team, trans_idx)
            #transition_objects.append(transition)
            #gameId_list.append(gameId)
            #team_list.append(team)
            
            all_poss_summaries = pd.concat([all_poss_summaries, possession_summaries], ignore_index=True)
            all_pass_stats = pd.concat([all_pass_stats, pass_stats], ignore_index=True)
            all_drive_stats = pd.concat([all_drive_stats, drive_stats], ignore_index=True)
            
            # with open(save_loc+'possessions_tracking_data/'+gameId+'_'+teamName+'.pkl', 'wb') as file:
            #     pickle.dump(transition, file)

    # #save the data
    # all_pass_stats.to_pickle(save_loc+'/pass_stats.pkl')
    # all_drive_stats.to_pickle(save_loc+'/drive_stats.pkl')
    all_poss_summaries.to_pickle(save_loc+'/possession_summaries.pkl')

    
def main():
    get_all_games_data()
    
    
main()
