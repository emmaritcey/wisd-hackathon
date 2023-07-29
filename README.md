Setup:
>>> pip install -r requirements.txt

Download data from AWS:
>>> python3 download_data.py
- saves event and tracking data in data/games/gameId folders
- saves metadata in data/metadata folder

Get transition stats and passing stats:
>>> python3 get_transition_stats.py
- saves transition possession summaries in data/transition/possession_summaries.pkl
- saves transition passing stats in data/transition/pass_stats.pkl
- saves transition drive stats in data/transition/drive_stats.pkl
- saves all transition tracking data in data/transition/possessions_tracking/


To run Streamlit Application in web browser:
>>> streamlit run Home.py
- if on Mac, may need to first install Xcode command line tools:
>>> xcode-select --install

