# Sersi
Sersi is a Discord bot purpose-built for Adam Something Central, to assist in moderation, and to provide functionality other bots couldn't deliver.  
Sersi requires Python 3.10.

## Commands
A list of commands can be triggered by running the `help` command, e.g:

```
s!help
```

## Self hosting
While we won't offer help with self-hosting Sersi (however, do report bugs!), this should serve as a simple guide to get it set up for your servers.  
Even though Sersi is kept to a single server, all cogs are built to support multiple servers.

### Folder structure
The folder structure is as follows:

| Folder name | Purpose |
|---|---|
| `cogs` | Contains all cogs. Cogs can be prevented from loading within the configuration. |
| `configuration` | Contains data classes pertaining to the configuration. |
| `data` | Contains static data. Also serves as a storage point for the database, which contains data that is intended to change. |
| `database` | Contains management and data classes pertaining to the database. |
| `utilities` | Contains utility scripts, providing commonly used functions used across code. |

The most relevant folder right now is `data`.

### Configuring Sersi
Make a copy of `config.example.yml` and rename it to `config.yml`.

```yml
# Default configuration; no IDs nor a token have been set.

token:    "Token here"

database:    "Sersi.db"
port:        8113
author_list: "authors.md"

prefix:   "s!"

activity: "Sword and Shield"

# ...
```

You want to change, at least, the token for your previously set up bot.  
In case you haven't done that yet, [do it right now](https://discord.com/developers/applications).

Refer to the code within the `configuration` folder for more information.  
All paths are relative of the `data` folder.

### Running Sersi
Simply launch `main.py`.
