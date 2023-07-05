#%%
from src.utils.data_helpers import get_data_liveTO, get_data_FGM
# %%
from src.preprocess.load_data import load_file
tracking_df = load_file('data/games/0042100404/0042100404_tracking.jsonl')
events_df = load_file('data/games/0042100404/0042100404_events.jsonl')

from nba_api.stats.endpoints import playbyplay
pbp_df = playbyplay.PlayByPlay("0042100404").get_data_frames()[0]
# %%
event_pbp_df = events_df.merge(pbp_df, left_on="pbpId", right_on="EVENTNUM", how="left")
#%%
team = 'home'
event_df, tr_df = get_data_FGM(event_pbp_df, tracking_df, team)
# %%

