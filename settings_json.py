import json

settings_json = json.dumps([
    {'type': 'title',
     'title': 'example title'},
    {'type': 'options',
     'title': 'Select Video Source',
     'desc': 'Choose your video source',
     'section': 'Video Settings',
     'options': ['option1', 'option2', 'option3'],
     'key': 'source'}])