from nba_api.stats.endpoints import playbyplay
from src.preprocess.load_data import load_file

class Game:
    def __init__(self, game_id):
        self.id = game_id
        
        
    def get_playbyplay(self):
        pbp_df = playbyplay.PlayByPlay(self.id).get_data_frames()[0]
        return pbp_df
    
    def get_events(self):
        game_id = self.id
        events_df = load_file('data/games/' + game_id + '/' + game_id + '_events.jsonl')
        return events_df
    
    def get_tracking(self):
        game_id = self.id
        tracking_df = load_file('data/games/' + game_id + '/' + game_id + '_tracking.jsonl')
        return tracking_df
        
    