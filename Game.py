from nba_api.stats.endpoints import playbyplay
from src.preprocess.load_data import load_game_file, load_metadata
from src.utils.data_helpers import get_team_name, get_team_directions
import json

class Game:
    def __init__(self, game_id):
        self.game_id = game_id
        self.pbp_df = self.get_playbyplay()
        self.events_df = self.get_events()
        self.tracking_df = self.get_tracking()
        self.event_pbp_df = self.merge_events_with_pbp()
        self.meta_data = self.get_metadata()
        
        
    def get_playbyplay(self):
        pbp_df = playbyplay.PlayByPlay(self.game_id).get_data_frames()[0]
        return pbp_df
    
    def get_events(self):
        game_id = self.game_id
        events_df = load_game_file('data/games/' + game_id + '/' + game_id + '_events.jsonl')
        return events_df
    
    def get_tracking(self):
        game_id = self.game_id
        tracking_df = load_game_file('data/games/' + game_id + '/' + game_id + '_tracking.jsonl')
        return tracking_df
        
    def merge_events_with_pbp(self):
        pbp_df = self.pbp_df
        events_df = self.events_df
        pbp_df = self.pbp_df
        events_df = self.events_df
        event_pbp_df = events_df.merge(pbp_df, left_on="pbpId", right_on="EVENTNUM", how="left")
        return event_pbp_df
    
    def get_metadata(self):
        '''
        get the metadata for the game from the metadata/games.json file
        add the name's of the teams 
        '''
        game_id = self.game_id
        event_pbp_df = self.event_pbp_df
        tracking_df = self.tracking_df
        
        all_games_md = load_metadata('data/metadata/games.json')
        all_games_md = all_games_md['games']
        game_md = list(filter(lambda game: game['nbaId'] == game_id, all_games_md))[0]
    
        game_md['awayTeamName'] = get_team_name(game_md['awayTeamId'])
        game_md['homeTeamName'] = get_team_name(game_md['homeTeamId'])
        
        home_direction1, home_direction2, away_direction1, away_direction2 = get_team_directions(event_pbp_df, tracking_df)
        game_md['homeDirection'] = (home_direction1, home_direction2)
        game_md['awayDirection'] = (away_direction1, away_direction2)
        
        if game_id[0:-1] == '004210030':
            game_md['series'] = 'ECF'
            if game_id == '0042100301':
                game_md['homeScore'] = 118
                game_md['awayScore'] = 107
            elif game_id == '0042100302':
                game_md['homeScore'] = 102
                game_md['awayScore'] = 127
            elif game_id == '0042100303':
                game_md['homeScore'] = 103
                game_md['awayScore'] = 109
            elif game_id == '0042100304':
                game_md['homeScore'] = 102
                game_md['awayScore'] = 82
            elif game_id == '0042100305':
                game_md['homeScore'] = 80
                game_md['awayScore'] = 93
            elif game_id == '0042100306':
                game_md['homeScore'] = 103
                game_md['awayScore'] = 111
            elif game_id == '0042100307':
                game_md['homeScore'] = 96
                game_md['awayScore'] = 100
                
        elif game_id[0:-1] == '004210031':
            game_md['series'] = 'WCF'
            if game_id == '0042100311':
                game_md['homeScore'] = 112
                game_md['awayScore'] = 87
            elif game_id == '0042100312':
                game_md['homeScore'] = 126
                game_md['awayScore'] = 112
            elif game_id == '0042100313':
                game_md['homeScore'] = 100
                game_md['awayScore'] = 109
            elif game_id == '0042100314':
                game_md['homeScore'] = 119
                game_md['awayScore'] = 109
            elif game_id == '0042100315':
                game_md['homeScore'] = 120
                game_md['awayScore'] = 110
        else:
            game_md['series'] = 'Finals'
            if game_id == '0042100401':
                game_md['homeScore'] = 108
                game_md['awayScore'] = 120
            elif game_id == '0042100402':
                game_md['homeScore'] = 107
                game_md['awayScore'] = 88
            elif game_id == '0042100403':
                game_md['homeScore'] = 116
                game_md['awayScore'] = 100
            elif game_id == '0042100404':
                game_md['homeScore'] = 97
                game_md['awayScore'] = 107
            elif game_id == '0042100405':
                game_md['homeScore'] = 104
                game_md['awayScore'] = 94
            elif game_id == '0042100406':
                game_md['homeScore'] = 90
                game_md['awayScore'] = 103
                
        if game_md['homeScore'] > game_md['awayScore']:
            game_md['homeWin'] = True
            game_md['awayWin'] = False
        else:
            game_md['homeWin'] = False
            game_md['awayWin'] = True
            
        return game_md 