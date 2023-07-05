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
len(event_df)

# %%
len(tr_df)
# %%
#get play by play data of all missed FGA
missed_fg_df = event_pbp_df[event_pbp_df['EVENTMSGTYPE'] == 2]

#get either all of the home team's missed FGA or all of the away team's missed FGA
if team == 'home':
    description1 = 'VISITORDESCRIPTION'
else:
    description1 = 'HOMEDESCRIPTION'
missed_fg_df = missed_fg_df[missed_fg_df[description1].str.contains('MISS')==True]
# %%
missed_fg_df
# %%
reb_all = event_pbp_df.iloc[missed_fg_df.index + 1] #all rebounds off team's missed FGs
# %%
if team == 'home':
    description2 = 'HOMEDESCRIPTION'
else:
    description2 = 'VISITORDESCRIPTION'
reb_def = reb_all[reb_all[description2].str.contains('REBOUND')==True]
# %%
len(reb_def)
# %%
reb_def
# %%
reb_def_tr = tracking_df[tracking_df['wallClock'].isin(reb_def['wallClock'].values)]

# %%
len(reb_def_tr)
# %%
