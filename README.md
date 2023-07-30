# WISD Hackathon
This code in this repository is part of a submission to the WISD Hackacthon. The purpose of this project was to perform analysis on teams transition tendencies by assessing their passing and driving habits.


## Setup/Installation Requirements
The only requirements for this code are a computer, internet connection, and Python 3.0 or above
To begin, download the repository and create a virtual environment. 
To install required libraries to virtual environment, run: 
```bash
python3 -m pip install -r requirements.txt
```
If on Mac, may need to also install Xcode command line tools to run Streamlit:
```bash
xcode-select --install
```

## Download Data
To download the data from AWS:
```bash
python3 download_data.py
```
* saves event and tracking data in data/games/gameId folders
* saves metadata in data/metadata folder

## Preprocess Data
To get transition data and stats:
```bash
python3 get_transition_stats.py
```
* saves transition possession summaries in data/transition/possession_summaries.pkl
* saves transition passing stats in data/transition/pass_stats.pkl
* saves transition drive stats in data/transition/drive_stats.pkl
* saves all transition tracking data in data/transition/>>>possessions_tracking/


To run Streamlit Application in web browser:
```bash
>>>streamlit run transition_app/Home.py
```

