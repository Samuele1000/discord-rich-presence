# Discord Activity

A small terminal tool that lets you set your own Discord Rich Presence ("Playing ...", "Watching ...") with presets or fully custom text.

## Features

- Interactive prompts in your terminal, no code editing needed
- Built-in presets: GTA VI, FiveM, Watching YouTube, Watching Twitch
- Fully custom mode: top/bottom line, images, timer (elapsed or countdown), party size, up to 2 buttons
- Remembers your last answers
- Easy to add your own presets (see below)

## Requirements

- Python 3.8 or newer
- The Discord **desktop app** running (the web version does not work)
- A free Discord application (see Setup)

## Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**.
   The **name of the application is the title Discord shows** in your activity (e.g. "Playing *Name*").
2. Copy the **Application ID** (this is your Client ID).
3. (Optional) Under **Rich Presence -> Art Assets**, upload images and give them a name. You can use those names as image keys.
4. Install the dependency:

   ```
   pip install -r requirements.txt
   ```

## Usage

```
python discord_activity.py
```

On Windows you can also double-click `start_discord_activity.bat`, which installs the dependency and starts the script.

Paste your Client ID the first time (it is saved locally), pick a preset or choose `0` for a fully custom activity. Keep the terminal window open, otherwise the activity disappears.

## Adding your own presets

Open `discord_activity.py` and edit the `PRESETS` list. Example:

```python
{
    "name": "Minecraft",
    "type": "playing",            # playing | watching | listening | competing
    "questions": [
        ("world", "World name", "Survival"),
    ],
    "details": "Playing Minecraft",
    "state": "World: {world}",    # {world} is replaced with your answer
    "timer": "start",             # "start" = elapsed time, "none" = no timer
    "large_image": "",            # Art Asset key or https URL (optional)
    "large_text": "Minecraft",
}
```

If an answer is left empty, any line that uses it is omitted.

## Troubleshooting

- **Nothing shows up:** check Discord -> Settings -> Activity Privacy and make sure activity sharing is on, and your status isn't Invisible. Discord and the script should both run as a normal user (or both as admin).
- **"Could not connect to Discord":** start the Discord desktop app first.
- **Title is wrong:** it's the application name in the Developer Portal. Rename the application and restart Discord.
- **Activity doesn't appear after adding images:** the image key probably doesn't match an uploaded Art Asset. Remove it or fix the name.
- **"Watching" type has no effect:** update the library with `pip install -U pypresence`.
- **Pylance "Import could not be resolved":** install the package for the interpreter VS Code uses (`Python: Select Interpreter`).

## Notes

Your Client ID and last answers are stored in `discord_activity_config.json` next to the script. This file is ignored by git, so it won't be uploaded by accident.

Built with [pypresence](https://github.com/qwertyquerty/pypresence). Not affiliated with or endorsed by Discord. Game and service names used in presets belong to their respective owners.