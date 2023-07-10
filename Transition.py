from Game import Game
from src.utils.data_helpers import get_data_DREB, get_data_liveTO, get_data_FGM, classify_possession
import pandas as pd
import numpy as np

class Transition(Game):
    def __init__(self, game_id, team):
        Game.__init__(self, game_id)
        self.team = team #'home' or 'away'
        #self.event_trans_opp, self.tracking_trans_opp = self.get_trans_opportunities()
        self.event_trans_opp = self.get_trans_opportunities()
        self.event_trans_opp, self.trans_possesions = self.get_possession_types()
        
    def get_trans_opportunities(self):
        '''
        Get the event data for all transition opportunities for specified team in Game
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
        #tracking_trans_opp = pd.concat([tracking_liveTO, tracking_FGM, tracking_Dreb])
        
        #return event_trans_opp, tracking_trans_opp
        return event_trans_opp
    
    
    #TODO: don't have to keep track/return of tracking data for all these --> can join the tables when needed
    
    def get_trans_possession(self, row_idx):
        '''
        Get an entire possession with a transition opportunity (8 seconds)
        To call: create a transition object --> trans_opp = Transition('0042100406', 'home')
                 iterate through 0 and n (n = # of transition opportunities)
                 pass trans_opp into get_trans_possession, along with the index of the transition opportunity you want

        INPUT:
            - trans_opp, df: the transition event/pbp dataframe (all of the first frame of transition opportunities for a single team, ex created by calling: trans_opp = Transition('0042100406', 'home'))
        OUTPUT:
            - trans_poss, df: 8 seconds of data following the start of a transition opportunity (trans_opp), contains tracking and event data 
        '''
        #get the transition opportunities from the game
        trans_opp = self.event_trans_opp
        #get tracking and event data from the entire game
        all_tracking_df = self.tracking_df
        all_event_df = self.event_pbp_df
        
        #get event data of the transition opportunity
        trans_event = trans_opp.loc[row_idx]

        #get the event number of this first transition opportunity
        eventNum = trans_event['EVENTNUM']

        #get the game clock value when this transition opportunity occurred
        trans_wallClock = all_event_df[all_event_df['EVENTNUM']==eventNum]['wallClock'].values[0]

        #get the index of this transition opportunity in the tracking df
        trans_idx = all_tracking_df[all_tracking_df['wallClock']==trans_wallClock].index[0]

        #get the next 200 frames (approximately 8 seconds of play)
        snapshot = all_tracking_df.iloc[trans_idx:trans_idx+200]

        #merge the 8 seconds of event data with the corresponding tracking data
        trans_poss = snapshot.merge(all_event_df, left_on="wallClock", right_on="wallClock", how="left")
        
        return trans_poss
    
    
    def get_possession_types(self):
        '''
        for each transition opportunity (row of self.event_trans_opp), call 'classify_possession' to determine outcome of possession
        add the outcome as a new column to self.event_trans_opp and return to update it
        store all 200 frames of each transition possession in a list
        OUTPUT:
            - event_trans_opp, df: updated event_trans_opp to include outcome column
            - all_trans_poss, list of df's: stores df for each transition possession
                -- first row in event_trans_opp corresponds to first df in all_trans_poss
        '''
        event_trans_opp = self.event_trans_opp
        
        outcome = []
        all_trans_poss = []
        for index, row in event_trans_opp.iterrows():
            trans_poss = self.get_trans_possession(index)
            all_trans_poss.append(trans_poss)
            trans_class = classify_possession(trans_poss)
            outcome.append(trans_class) 
        event_trans_opp['OUTCOME'] = outcome
        
        return event_trans_opp, all_trans_poss
    
