from nba_api.stats.endpoints import playbyplay
from src.preprocess.load_data import load_game_file, load_metadata
from src.utils.data_helpers import get_team_name, get_team_directions
import json

#TODO: find direction each team is going to start the game and the second half
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

        return game_md