# discord-cli

## Dependencies

[Python>=3.9](https://python.org/)  

    discord.py>=1.6.0

## keys.json

| attribute |                   value                  | type      |
|-----------|------------------------------------------|-----------|
| token     | Discord auth header / bot token | string | string    |

## Run

    python main.py

## config.json

| attribute          |                   value                  | type          |
|--------------------|------------------------------------------|---------------|
| prefix             | command prefix                           | string        |
| current_guild_id   | Optional initial guild id                | number / null |
| current_channel_id | Optional initial channel id              | number / null |
| chat_log           | Log Discord channel messages?            | boolean       |
| bot                | User or Bot account?                     | boolean       |
