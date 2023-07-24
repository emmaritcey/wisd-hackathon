
import os
import json
from nba_api.stats.static import teams
import numpy as np

METADATA_PATH = './data/metadata'

#TODO: calculate number of games each team played --> loop through games, have counter for each team


#TODO: could change this function so that it returns meta data for a game --> function input is the game id of the game we want the meta data for
def get_game_meta_data():
    '''
    get metadata for our 18 games using game id's
    RETURN:
    - games_md: a list of dictionaries of the metadata for the 18 playoff games we're looking at
    '''
    
    #get all game ID's
    game_ids = os.listdir("./data/games/")

    #get metadata for ALL games
    with open(METADATA_PATH + '/games.json') as f:
        all_games_md = json.load(f)['games']

    #keep metadata only for our 18 games
    games_md = [] 
    for game in all_games_md:
        if game['nbaId'] in game_ids:
            games_md.append(game)
            
    return games_md



def get_team_name(teamID):
    '''
    get team ID from the game metadata dictionary
    INPUT:
     - teamID: NBA ID of a single team of interest (ex. access away team's ID from first game via #teamID = games_md[0]['awayTeamId'])
    RETURN:
     - team_name: name of the team with NBA ID teamID 
    '''
    
    #get team names using team ID's
    with open(METADATA_PATH + '/teams.json') as f:
        all_teams = json.load(f)['teams']
        
    for team in all_teams:
        if team['id'] == teamID:
            team_name = team['name']
            break
        
    return team_name


def get_team_id(teamName):
    '''
    get the team ID given the team name
    get all NBA teams from nba_api
    INPUT:
        - teamName: string
    RETURN:
        - team ID: string
    '''
    nba_teams = teams.get_teams()
    team_info = [team for team in nba_teams if team['full_name'] == teamName][0]
    team_id = team_info['id']
    return team_id


def get_player_name(playerID):
    '''
    get player name using player ID
    INPUT:
    - playerID: ID of player you want the name of
    RETURN:
    - player_name
    '''

    with open(METADATA_PATH + '/players.json') as f:
        all_players = json.load(f)['players']
        
    for player in all_players:
        if player['id'] == playerID:
            player_name = player['firstName'] + ' ' + player['lastName']
            break
        
    return player_name

'''
PROBABLY DON'T NEED
'''
def get_event(pbp_event, event_type, events_df, tracking_df):
    '''
    given an event from the play-by-play data, find the corresponding row in the event data and tracking data
    event_df contains pbpId that matches EVENTNUM in play-by-play data
    tracking_df can be matched to row in event_df by matching the wallClock values
    INPUT:
        - pbp_event, series: a single row from the play-by-play df representing an event of interest
        - event_type, str: type of event (ex. 'SHOT', 'REB', 'FT', 'TO')
        - events_df, DF: all event data from the game
        - tracking_df, DF: all tracking data from the game
    '''
    play_id = pbp_event['EVENTNUM']
    event = events_df[(events_df['pbpId']==play_id) & (events_df['eventType']==event_type)] #sometimes the pass into the shot is given same pbpId, so specifially search for event of interest
    tr_event = tracking_df[tracking_df['wallClock']==event['wallClock'].values[0]]
    return event, tr_event


def get_data_liveTO(event_pbp_df, tracking_df, team):
    '''
    get the event data and tracking data for all live turnovers in a game for one team
    INPUT:
        - event_pbp_df, DF: all event data from the game merged with the play-by-play data
        - tracking_df, DF: all tracking data from the game
        - team, str: 'home' to get home team's fgm or 'away' to get visiting team's fgm
    RETURN:
        - live_TO_event: event data (and pbp data) containing all live ball turnovers for one team
        - live_TO_tr: tracking data at the exact moment each turnover occurred for one team
    '''
    live_TO_all = event_pbp_df[(event_pbp_df['EVENTMSGTYPE']==5) & ((event_pbp_df['EVENTMSGACTIONTYPE']==1) | (event_pbp_df['EVENTMSGACTIONTYPE']==2))]
    if team == 'home':
        description1 = 'HOMEDESCRIPTION'
    else:
        description1 = 'VISITORDESCRIPTION'
    live_TO_event = live_TO_all[live_TO_all[description1].str.contains('Turnover')==True]
    live_TO_tr = tracking_df[tracking_df['wallClock'].isin(live_TO_event['wallClock'].values)]
    return live_TO_event, live_TO_tr


def get_data_FGM(event_pbp_df, tracking_df, team):
    '''
    get the event data and tracking data for all made field goals in a game for one team
    INPUT:
        - event_pbp_df, DF: all event data from the game merged with the play-by-play data
        - tracking_df, DF: all tracking data from the game
        - team, str: 'home' to get home team's fgm or 'away' to get visiting team's fgm
    RETURN:
        - fgm_events, df: event data containing all made field goals for one team
        - fgm_tr, df: tracking data at the exact moment each field goal was made for one team
    '''   
    
    fgm_df = event_pbp_df[event_pbp_df['EVENTMSGTYPE']==1]
    
    #remove made FG's where foul occurred (AND 1 opportunities), since we're not including FT's as transition opportunities
    for index in fgm_df.index:
        if event_pbp_df['eventType'].iloc[index+1] == 'FOUL':
            fgm_df = fgm_df.drop(index)
            
    
    if team == 'home':
        description1 = 'HOMEDESCRIPTION'
    else:
        description1 = 'VISITORDESCRIPTION'
    fgm_df = fgm_df[fgm_df[description1].notnull()] #if home team took shot, HOMEDESCRIPTION contains description, if visitor team took shot then its null
    fgm_events = fgm_df[fgm_df['eventType']=='SHOT']#sometimes the pass into the shot is given same pbpId, so specifially search for event of interest
    fgm_tr = tracking_df[tracking_df['wallClock'].isin(fgm_events['wallClock'].values)]
    return fgm_events, fgm_tr


def get_data_DREB(event_pbp_df, tracking_df, team):
    '''
    get the event data and tracking data for all defensive rebounds for one team in a game
    INPUT:
        - event_pbp_df, DF: all event data from the game merged with the play-by-play data
        - tracking_df, df: all tracking data from the game
        - team, str: 'home' to get home team's defensive rebounds or 'away' to get visiting team's defensive rebounds
    RETURN:
        - reb_def_events: event data containing all defensive rebounds for one team
        - reb_def_tr: tracking data at the exact moment each defensive rebound was obtained for one team
    '''
    #get play by play data of all missed FGA
    missed_fg_df = event_pbp_df[event_pbp_df['EVENTMSGTYPE'] == 2]
    
    #get either all of the home team's missed FGA or all of the away team's missed FGA
    if team == 'home':
        description1 = 'VISITORDESCRIPTION'
    else:
        description1 = 'HOMEDESCRIPTION'
    missed_fg_df = missed_fg_df[missed_fg_df[description1].str.contains('MISS')==True]
    
    #find defensive rebounds from team's missed shots
    reb_all = event_pbp_df.iloc[missed_fg_df.index + 1] #all rebounds off team's missed FGs
    if team == 'home':
        description2 = 'HOMEDESCRIPTION'
    else:
        description2 = 'VISITORDESCRIPTION'
    reb_def = reb_all[reb_all[description2].str.contains('REBOUND')==True]
    
    reb_def_tr = tracking_df[tracking_df['wallClock'].isin(reb_def['wallClock'].values)]
    
    return reb_def, reb_def_tr


def classify_possession(trans_possession):
    '''
    Determine whether a (transition) opportunity ended with a shot, turnover, stoppage, or no shot
        - shot = shot taken within snapshot (8 seconds)
        - stoppage = out of bounds, violation, etc
        - turnover = turnover before shot was taken
        - no shot = no shot, stoppage, or turnover within the snapshot (8 seconds)
    INPUT:
        - trans_possesion, df: dataframe containing 200 frames (about 8 seconds) of event and tracking data for a single transition opportunity
    OUTPUT:
        - possession class, str: 'shot', 'stoppage', 'turnover', 'no shot'
        - min_idx, int: index corresponding to the possession class event, ie the end of the transition possession (shot, stoppage, etc)
    '''
    stoppage = False
    stoppage_idx = -10
    tover = False
    tover_idx = -10
    shot = False
    shot_idx = -10
    foul = False
    foul_idx = -10
    
    possession_class = None
    
    events_idx_dict = {}
    
    #if clock stopped during this possession, find the index of where it stopped
    if True in trans_possession['gameClockStopped'].values:
        stoppage_idx = np.where(trans_possession['gameClockStopped'].values == True)[0][0]
        stoppage = True
        events_idx_dict['stoppage'] = stoppage_idx
        
    trans_events = trans_possession['eventType'].values[1:]

    #find if turnover occurred
    if 'TO' in trans_events:
        tover_idx = np.where(trans_events == 'TO')[0][0] + 1
        tover = True
        events_idx_dict['turnover'] = tover_idx

    #find if foul occurred
    if 'FOUL' in trans_events:
        foul_idx = np.where(trans_events == 'FOUL')[0][0] + 1
        foul = True
        events_idx_dict['foul'] = foul_idx
        
    #find if shot was taken
    if 'SHOT' in trans_events:
        shot_idx = np.where(trans_events == 'SHOT')[0][0] + 1
        shot = True
        events_idx_dict['shot'] = shot_idx
    
    if len(events_idx_dict) == 0: #no stoppage, turnover, foul, or shot
        possession_class = 'no shot'
        min_idx = len(trans_possession) - 1
        
    else:
        min_idx = min(events_idx_dict.values())
        possession_class = [key for key in events_idx_dict if events_idx_dict[key] == min_idx][0]
            
    if possession_class == 'shot':
        outcome_msg = trans_possession['EVENTMSGTYPE'].iloc[min_idx]
        outcome_msgaction = trans_possession['EVENTMSGACTIONTYPE'].iloc[min_idx]
    else:
        outcome_msg = np.nan
        outcome_msgaction = np.nan
    
    
    return possession_class, min_idx, outcome_msg, outcome_msgaction


def get_team_directions(event_pbp_df, tracking_df):
    '''
    get the direction the team is going
    INPUT:
        - event_pbp_df, DF: all event data from the game merged with the play-by-play data
        - tracking_df, df: all tracking data from the game):
    OUTPUT:
        - home/away_side1/2: 1 = shooting on positive x side (right), -1 = shooting on negative x side (left)
    '''
    
    first_shot = event_pbp_df[event_pbp_df['eventType']=='SHOT'].iloc[0]
    if first_shot['HOMEDESCRIPTION'] is not None: 
        if 'FOUL' in first_shot['HOMEDESCRIPTION']: #away team took shot (home team fouled)
            team = 'away'
        else: #home team took shot
            team = 'home' 
    else: # first_shot['VISITORDESCRIPTION'] is not None: 
        if 'FOUL' in first_shot['VISITORDESCRIPTION']: #home team took shot (away team fouled)#away team took shot
            team = 'home'
        else: 
            team = 'away'
    time_of_shot = event_pbp_df[event_pbp_df['eventType']=='SHOT'].iloc[0]['wallClock']

    ball_location = tracking_df[tracking_df['wallClock'] == time_of_shot]['ball'].iloc[0]

    #if ball is in positive x location --> this team is shooting on the right/positive end, if negative then shooting on left/negative side
    #1/2 indicates 1st/2nd half
    if (ball_location[0] > 0 and team == 'home') or (ball_location[0] < 0 and team == 'away'):
            home_side1 = 1
            home_side2 = -1
            away_side1 = -1
            away_side2 = 1
    if  (ball_location[0] > 0 and team == 'away') or (ball_location[0] < 0 and team == 'home'):    
            home_side1 = -1
            home_side2 = 1
            away_side1 = 1
            away_side2 = -1  
            
    return home_side1, home_side2, away_side1, away_side2


def travel_dist(locations):
    '''
    calculate the total euclidean distance the object has travelled by calculating each consecutive euclidean distance
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


def travel_dist_1d(locations):
    ''''
    get the total x distance and total y distance the object has travelled by calculating each consective difference and summing the values
    '''
    # get the differences of each consecutive value in each sublist
    diff = np.diff(locations, axis=1)
    dist = np.abs(diff).sum(axis=1)
    
    return round(dist[0],2), round(dist[1],2)