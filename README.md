## About
My 9th grade was fully online, and sometimes, 14-year-olds just want to be annoying. My friends and I wanted a way to moderate users without kicking or banning them, and instead opt for simply restricting their activity for a set period of time.

The Warden is a custom Discord bot who's main feature is the ability to give users a pre-set role and automatically remove it after a timer runs out, which was useful for operating a time-out system in the server The Warden was developed for. During time-out, users would be restricted to talking to the moderators.

Other features:
- Join a voice channel, and play Rick Astley's "Never Gonna Give You Up"
- Webscrape for data on Covid-19 cases in Washtenaw County
- "Snipe" the most recently deleted message
- Features can be toggled on and off

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

## Contributing
The Warden is actively being developed and contributions are always welcome

List of features to implement:
- Play music from YouTube playlists
- Track covid cases in AAPS specfically
- Display the current uptime

## License
[MIT](https://choosealicense.com/licenses/mit/)
