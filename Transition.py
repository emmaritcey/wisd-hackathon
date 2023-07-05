from Game import Game
from src.utils.data_helpers import get_data_DREB, get_data_liveTO, get_data_FGM
import pandas as pd

class Transition(Game):
    def __init__(self, game_id, team):
        Game.__init__(self, game_id)
        self.team = team #'home' or 'away'
        self.event_trans_opp, self.tracking_trans_opp = self.get_trans_opp()
        
        
    def get_trans_opp(self):
        '''
        Get all transition opportunities for specified team in Game
        '''
        team = self.team
        tracking_df = self.tracking_df
        event_pbp_df = self.event_pbp_df
        
        event_Dreb, tracking_Dreb = get_data_DREB(event_pbp_df, tracking_df, team)
        
        if team == 'home': #if looking for home team's trans opps, then need away team's TO's and made Fg's, and vice versa
            use_team = 'away'
        else:
            use_team = 'home'
        event_liveTO, tracking_liveTO = get_data_liveTO(event_pbp_df, tracking_df, use_team)
        event_FGM, tracking_FGM = get_data_FGM(event_pbp_df, tracking_df, use_team)

        
        event_trans_opp = pd.concat([event_liveTO, event_FGM, event_Dreb])
        tracking_trans_opp = pd.concat([tracking_liveTO, tracking_FGM, tracking_Dreb])
        
        return event_trans_opp, tracking_trans_opp