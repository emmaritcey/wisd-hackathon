
import os
import json
from nba_api.stats.static import teams

METADATA_PATH = './data/metadata'



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


def get_data_liveTO(pbp_df, events_df, tracking_df, team):
    '''
    get the event data and tracking data for all live turnovers in a game for one team
    INPUT:
        - pbp_df, DF: play-by-play data from the game 
        - events_df, DF: all event data from the game
        - tracking_df, DF: all tracking data from the game
        - team, str: 'home' to get home team's fgm or 'away' to get visiting team's fgm
    RETURN:
        - live_TO_events: event data containing all live ball turnovers for one team
        - live_TO_tr: tracking data at the exact moment each turnover occurred for one team
    '''
    live_TO_all = pbp_df[(pbp_df['EVENTMSGTYPE']==5) & ((pbp_df['EVENTMSGACTIONTYPE']==1) | (pbp_df['EVENTMSGACTIONTYPE']==2))]
    if team == 'home':
        description1 = 'HOMEDESCRIPTION'
    else:
        description1 = 'VISITORDESCRIPTION'
    live_TO = live_TO_all[live_TO_all[description1].str.contains('Turnover')==True
                        ]
    live_TO_events = events_df[events_df['pbpId'].isin(live_TO['EVENTNUM'].values)]
    live_TO_tr = tracking_df[tracking_df['wallClock'].isin(live_TO_events['wallClock'].values)]
    return live_TO_events, live_TO_tr, live_TO


def get_data_FGM(pbp_df, events_df, tracking_df, team):
    '''
    get the event data and tracking data for all made field goals in a game for one team
    INPUT:
        - pbp_df, DF: play-by-play data of the game
        - events_df, DF: all event data from the game
        - tracking_df, DF: all tracking data from the game
        - team, str: 'home' to get home team's fgm or 'away' to get visiting team's fgm
    RETURN:
        - fgm_events, df: event data containing all made field goals for one team
        - fgm_tr, df: tracking data at the exact moment each field goal was made for one team
    '''   
    
    fgm_df = pbp_df[pbp_df['EVENTMSGTYPE']==1]
    if team == 'home':
        description1 = 'HOMEDESCRIPTION'
    else:
        description1 = 'VISITORDESCRIPTION'
    fgm_df = fgm_df[fgm_df[description1].notnull()] #if home team took shot, HOMEDESCRIPTION contains description, if visitor team took shot then its null
    play_id = fgm_df['EVENTNUM'].values
    fgm_events = events_df[(events_df['pbpId'].isin(play_id)) & (events_df['eventType']=='SHOT')] #sometimes the pass into the shot is given same pbpId, so specifially search for event of interest
    fgm_tr = tracking_df[tracking_df['wallClock'].isin(fgm_events['wallClock'].values)]
    return fgm_events, fgm_tr, fgm_df


def get_data_DREB(pbp_df, events_df, tracking_df, team):
    '''
    get the event data and tracking data for all defensive rebounds for one team in a game
    INPUT:
        - pbp_df, df: all play-by-play data of the game
        - events_df, df: all event data from the game
        - tracking_df, df: all tracking data from the game
        - team, str: 'home' to get home team's defensive rebounds or 'away' to get visiting team's defensive rebounds
    RETURN:
        - reb_def_events: event data containing all defensive rebounds for one team
        - reb_def_tr: tracking data at the exact moment each defensive rebound was obtained for one team
    '''
    #get play by play data of all missed FGA
    missed_fg_df = pbp_df[pbp_df['EVENTMSGTYPE'] == 2]
    
    #get either all of the home team's missed FGA or all of the away team's missed FGA
    if team == 'home':
        description1 = 'VISITORDESCRIPTION'
    else:
        description1 = 'HOMEDESCRIPTION'
    missed_fg_df = missed_fg_df[missed_fg_df[description1].str.contains('MISS')==True]
    
    #find defensive rebounds from team's missed shots
    reb_all = pbp_df.iloc[missed_fg_df.index + 1] #all rebounds off team's missed FGs
    if team == 'home':
        description2 = 'HOMEDESCRIPTION'
    else:
        description2 = 'VISITORDESCRIPTION'
    reb_def = reb_all[reb_all[description2].str.contains('REBOUND')==True]
    
    reb_def_events = events_df[events_df['pbpId'].isin(reb_def['EVENTNUM'].values)]
    reb_def_tr = tracking_df[tracking_df['wallClock'].isin(reb_def_events['wallClock'].values)]
    
    return reb_def_events, reb_def_tr, reb_def