# SC2Notes
### [Download](https://github.com/leigholiver/sc2notes/releases/latest)

##### Usage
Download and run `sc2notes.exe`
Copy the `SC2Switcher URL` into the Webhook tab of the [SC2Switcher obs-studio plugin](https://github.com/leigholiver/OBS-SC2Switcher) or [SC2Switcher Standalone](https://github.com/leigholiver/SC2Switcher-Standalone)

Make sure that 'Webhook enabled' is ticked in SC2Switcher and you have entered your username into the Usernames tab

When a game starts your notes and match history against your opponent should be displayed.

Your notes and match history are stored in `notes.json` and `matches.json` respectively if you want to back them up.

##### Build instructions
`pip install -r requirements.txt`
`pyinstaller main.py --noconsole --name sc2notes`