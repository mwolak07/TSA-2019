import json

settings_json = json.dumps([
    {'type': 'options',
     'title': 'Select Video Source',
     'desc': 'Choose your video source',
     'section': 'App Settings',
     'options': ['Pre-Recorded', 'Live Feed'],
     'key': 'source'},
     {'type': 'path',
     'title': 'Choose Pre-Recorded File',
     'desc': 'Locate the video file you would like to analyze',
     'section': 'App Settings',
     'key': 'path'},
     {'type': 'string',
     'title': 'Emergency Email Contacts',
     'desc': 'Enter emergency contact emails, seperated by a comma and a space',
     'section': 'App Settings',
     'key': 'emails'},
     {'type': 'string',
     'title': 'Emergency Phone Numbers',
     'desc': 'Enter emergency phone numbers, seperated by a comma and a space',
     'section': 'App Settings',
     'key': 'numbers'}
     ])