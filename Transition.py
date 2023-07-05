from Game import Game
from src.utils.data_helpers import get_data_DREB, get_data_liveTO, get_data_FGM

class Transition(Game):
    def __init__(self, game_id, team):
        Game.__init__(self, game_id)
        self.team = team #'home' or 'away'
        
        
    def get_trans_opp(self):
        pbp_df = self.get_playbyplay()
        
        #get_data_liveTO(event_pbp_df, tracking_df, team)