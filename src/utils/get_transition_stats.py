import pandas as pd
import numpy as np
from src.utils.pass_analysis import get_pass_data
from src.utils.data_helpers import get_team_name

from Transition import Transition
import os

#TODO: what time did the ball cross half at? (time elapsed to cross half)

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
    if poss_length == 0:
        print('oh no')
    
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


#TODO: if shot was taken in transition, add the type of shot taken and whether it was made or not
def get_poss_summary(possession_df, end_idx, event, team):
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
    OUTPUT:
        - summary_dict, dict: dictionary containing summary of a single transition possession
    
    '''
    #get length of possession in seconds
    poss_length = get_possession_length(possession_df, end_idx)
    #get number of dribbles
    num_dribbles, num_dribbles_per_sec = count_event(possession_df, 'DRIBBLE', end_idx, poss_length)
    #get number of passes
    num_passes, num_passes_per_sec = count_event(possession_df, 'PASS', end_idx, poss_length)
    
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
    summary_dict = {'Possession Length': poss_length, '# Dribbles': num_dribbles, '# Passes': num_passes, 
                    'Ball Distance': ball_dist, 'Average Ball Speed': avg_speed_ball, 'Off Player Distances': off_distances, 
                    'Off Player Speeds': off_speeds, 'Def Player Distances': def_distances, 'Def Player Speeds': def_speeds,
                    'Trigger': trigger, 'Outcome': outcome, 'OutcomeMSG': outcome_eventmsg, 'OutcomeMSGaction': outcome_eventmsgaction}
    
    return summary_dict


def get_all_poss_summaries(trans_possessions, end_indices, events_df, team, first_x_seconds = 8):
    '''
    create a list of dictionaries containing the summaries of each transition possession
    INPUT:
        - trans_possessions, list of df's: stores df for each transition possession (Transition.trans_possesions)
        - end_indices, list of ints: indices of the end of each transition possession (where the shot, TO, foul, stoppage, etc occurred)
        - events_df, df: dataframe containing event info for each transition opportunity
        - team, str: 'home' or 'away'
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
            trans_summaries.append(get_poss_summary(trans_possessions[i], end_indice, events_df.iloc[i], team))
        else: #looking at shorter range of time, say first three seconds of the possession
            time_end_indice = first_x_seconds*25 + 1 #25 frames per second
            if time_end_indice > end_indice: #transition possession ended before the chosen time
                trans_summaries.append(get_poss_summary(trans_possessions[i], end_indice, events_df.iloc[i], team))
            else: 
                trans_summaries.append(get_poss_summary(trans_possessions[i], time_end_indice, events_df.iloc[i], team))
        
    return trans_summaries
    

def get_pass_outcomes(all_poss_summaries):
    '''
    from the pass summary data, record the trigger/outcome for each pass to add to the pass analysis dataframe
    INPUT:
        - all_poss_summaries, dict: dict containing the summaries of each transition possession, created from get_all_poss_summaries()
    '''
    triggers = []
    outcomes = []
    outcomes_msg = []
    outcomes_msgaction = []

    for idx in range (0,len(all_poss_summaries)):
        n_passes = all_poss_summaries[idx]['# Passes']
        for jdx in range(0,n_passes):
            triggers.append(all_poss_summaries[idx]['Trigger'])
            outcomes.append(all_poss_summaries[idx]['Outcome'])
            outcomes_msg.append(all_poss_summaries[idx]['OutcomeMSG'])
            outcomes_msgaction.append(all_poss_summaries[idx]['OutcomeMSGaction'])
    
    return triggers, outcomes, outcomes_msg, outcomes_msgaction
            

    
def get_single_game_data(trans_object, team, first_x_seconds = 8, all_possessions = True):
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
        gameId = trans_object.meta_data['id']
        teamId = trans_object.meta_data['homeTeamId']
        #teamName = trans_object.meta_data['homeTeamName']
        #teamId = get_team_id(teamName)
    else:
        shooting_directions = trans_object.meta_data['awayDirection']
        gameId = trans_object.meta_data['id']
        teamId = trans_object.meta_data['awayTeamId']
        #teamName = trans_object.meta_data['awayTeamName']
        #teamId = get_team_id(teamName)
    
    
  
    trans_summaries = get_all_poss_summaries(possessions_tracking, end_of_possessions, possessions_event, team, first_x_seconds) 
    pass_df = get_pass_data(possessions_tracking, end_of_possessions, possessions_event, shooting_directions, team)
    
    #add the triggers/outcomes to each pass in pass_df
    triggers, outcomes, outcomes_msg, outcomes_msgaction = get_pass_outcomes(trans_summaries)
    pass_df['Transition Trigger'] = triggers
    pass_df['Outcome'] = outcomes
    pass_df['OutcomeMSG'] = outcomes_msg
    pass_df['OutcomeMSGaction'] = outcomes_msgaction
        
    #convert dictionary to dataframe 
    trans_summaries_df = pd.DataFrame(trans_summaries)
    
    #add team and game info to both dataframes
    trans_summaries_df['Team Id'] = teamId
    trans_summaries_df['Team Name'] = get_team_name(teamId)
    trans_summaries_df['Game Id'] = gameId
    pass_df['Team Id'] = teamId
    pass_df['Team Name'] = get_team_name(teamId)
    pass_df['Game Id'] = gameId
    
    
    return trans_summaries_df, pass_df

def get_all_games_data():
    transition_objects = []
    all_poss_summaries = pd.DataFrame()
    all_pass_stats = pd.DataFrame()
    idx = 0
    print('Getting transition data for game:')
    for gameId in os.listdir('data/games'):
        print(gameId)
        for team in ['home', 'away']:
            transition = Transition(gameId, team)
            possession_summaries, pass_stats = get_single_game_data(transition, team)
            transition_objects.append(transition)
            
            all_poss_summaries = pd.concat([all_poss_summaries, possession_summaries], ignore_index=True)
            all_pass_stats = pd.concat([all_pass_stats, pass_stats], ignore_index=True)
        idx += 1
    
    #save the data
    save_loc = 'data/transition'
    if os.path.isdir(save_loc) == False:
        os.mkdir(save_loc)

    all_pass_stats.to_csv(save_loc+'/pass_stats.csv', index=False)
    all_poss_summaries.to_csv(save_loc + '/possession_summaries.csv', index=False)
    
    
    
def main():
    get_all_games_data()
    
    
main()
