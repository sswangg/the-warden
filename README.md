<div align="center">
  <img src="https://i.imgur.com/zDCzeOH.png" align="center" width="450">
  <br>
  <strong><i>A unique moderation bot for Discord</i></strong>
  <br>
  <br>

  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Made%20With-Python%203.9-blue.svg?style=for-the-badge&logo=Python" alt="Made with Python 3.9">
  </a>

  <a href="https://github.com/sswangg/the-warden/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-mit-e74c3c.svg?style=for-the-badge" alt="MIT License">
  </a>
  
  <br>
  <br>
  <!--<img src="https://i.imgur.com/qJAn3KQ.png" align="center" width="700">-->
  <img src="https://i.imgur.com/QrPkRa8.png" align="center" width="600">

<br>
</div>

## About
The Warden is a custom bot who's main feature is the ability to give users a pre-set role and automatically remove it after a timer runs out, which is useful for operating the "honry jail" in the server The Warden was developed for. It can also send the most recently deleted message in a channel, act as a music bot, and remind you to go to online class.

Note that The Warden is not designed for useage in other servers, and there is no easy way to configure The Warden to suit your needs.

## Setup

Information on making a bot account can be found in the [discord.py documentation](https://discordpy.readthedocs.io/en/stable/discord.html). Once you've done that:

Clone the repo

```console
$ git clone https://github.com/sswangg/the-warden.git
$ cd the-warden
```

Create a file named `.env` with your token in the same directory as main.py
```
# .env
DISCORD_TOKEN=your-bot-token
```

Create a virtual environment and activate it

```console
$ python3 -m venv .
$ source bin/activate
```

Install dependancies

```console
$ pip3 install -r requirements.txt
```

And start The Warden

```console
$ python3 main.py
```

## Commands
owo help - send the help message
owo bonk - send a user to horny jail
owo banish - send a user to the shadow realm
owo release - release a user from horny jail/the shadow realm
owo s - send the most recently deleted message in a channel
owo es - send the most recntly edited in a channel, pre-edit
owo imbored - rickroll a voice channel
owo ping - send the latency

## Contributing
The Warden is actively being developed and contributions are always welcome

List of features I want to implement:
- Play music from YouTube playlists
- Track covid cases in AAPS
- Ping to remind people to go to class according to Pioneer's bell schedule
- Send a link to this discord repository
- Display the cureent uptime
- config.yaml file so that the bot is actually configurable
- Make the bot configurable through commands so that it can be released into the wild

Feel free to suggest a feature and maybe even offer some money with it.

## License
[MIT](https://choosealicense.com/licenses/mit/)
