import json

settings_json = json.dumps([
    {'type': 'options',
     'title': 'Select Video Source',
     'desc': 'Choose your video source',
     'section': 'App Settings',
     'options': ['Live Feed', 'Pre-Recorded'],
     'key': 'source'},
     {'type': 'path',
     'title': 'Choose Pre-Recorded File',
     'desc': 'Locate the video file you would like to analyze',
     'section': 'App Settings',
     'key': 'path'}
     ])