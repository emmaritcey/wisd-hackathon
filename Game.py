from nba_api.stats.endpoints import playbyplay
from src.preprocess.load_data import load_game_file, load_metadata
from src.utils.data_helpers import get_team_name
import json

class Game:
    def __init__(self, game_id):
        self.id = game_id
        
        
    def get_playbyplay(self):
        pbp_df = playbyplay.PlayByPlay(self.id).get_data_frames()[0]
        return pbp_df
    
    def get_events(self):
        game_id = self.id
        events_df = load_game_file('data/games/' + game_id + '/' + game_id + '_events.jsonl')
        return events_df
    
    def get_tracking(self):
        game_id = self.id
        tracking_df = load_game_file('data/games/' + game_id + '/' + game_id + '_tracking.jsonl')
        return tracking_df
        
    def merge_events_with_pbp(self):
        pbp_df = self.get_playbyplay()
        events_df = self.get_events()
        event_pbp_df = events_df.merge(pbp_df, left_on="pbpId", right_on="EVENTNUM", how="left")
        return event_pbp_df
    
    def get_metadata(self):
        '''
        get the metadata for the game from the metadata/games.json file
        add the name's of the teams 
        '''
        game_id = self.id
        all_games_md = load_metadata('data/metadata/games.json')
        all_games_md = all_games_md['games']
        game_md = list(filter(lambda game: game['nbaId'] == game_id, all_games_md))[0]
    
        game_md['awayTeamName'] = get_team_name(game_md['awayTeamId'])
        game_md['homeTeamName'] = get_team_name(game_md['homeTeamId'])

        return game_md