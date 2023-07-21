Setup:
>>> pip install -r requirements.txt

Download data from AWS:
>>> python3 download_data.py
- saves event and tracking data in data/games/gameId folders
- saves metadata in data/metadata folder

Get transition stats and passing stats:
>>> python3 get_transition_stats.py
- saves transition possession summaries in data/transition/possession_summaries.csv
- saves transition passing stats in data/transition/pass_stats.csv

