# Project 2

Project submission by peerky (edx username)

Web Programming with Python and JavaScript

This is an implementation of project 2 of the 2018 CS50W edx/harvard course following the specifications layed out here:

https://docs.cs50.net/web/2018/x/projects/2/project2.html

Personal touch:
Ability to translate the message from any language to English prior to sending using the globe icon.
This uses the textblob library, which itself uses google translate in the background for the translations, so the amount of translations that can be done will probably be limited withou a proper app account for it. I couldn't find more information about it, so use at yor own risk.

Minor additions or implementation details:
- User can logout, which empties the use variables in the browser and the flask app
- Room and user list vanish for resolutions < 600px width
- When trying to create a channel whose name already exists, the user is put in that channel wihout further ado.

This app is in no way secure, consistent or practical nor does it use the room / user logic built into socketio and broadcasts all messages from all rooms to all users on updates.

Youtube demonstration:


Files:
.
├── static
│   ├── helper_functions.js -> Mostly abreviations for queryselectores and console.log
│   ├── main.js -> Main js logic for login and main chat page
│   ├── style.css
│   ├── style.css.map
│   └── style.scss
├── templates
│   ├── index.html
│   ├── layout.html
│   └── login.html
├── .gitignore
├── application.py
├── config.py -> Just some config variables
├── README.md
├── requirements.txt
├── runapp.ps1 -> Powershell batch script to set env variables and start application
├── runapp.sh -> same for Bash
└── utils.py -> minor helper functions


