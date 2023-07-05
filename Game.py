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
        
    def merge_events_with_pbp(self):
        pbp_df = self.get_playbyplay()
        events_df = self.get_events()
        event_pbp_df = events_df.merge(pbp_df, left_on="pbpId", right_on="EVENTNUM", how="left")
        return event_pbp_df
    