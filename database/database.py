import sqlite3


# SQLite3 powered data storage, used to store all randomly accessible data.
class Database:
    # Loads in the database, with the given absolute path.
    def __init__(self, path: str):
        self.connection: sqlite3.Connection = sqlite3.connect(path)

        # TODO: set up database if it doesn't hold the tables we need

    # Commits all outstanding changes.
    def commit_changes(self):
        self.connection.commit()

    # Fetches the given channel from the database.
    #
    # Names can be found in the database scheme.
    def guild_get_logging_channel(self, guild_id: int, channel_type: str) -> int | None:
        result: sqlite3.Cursor = self.connection.execute(f"select {channel_type} from guild_preferences where guild_id = {guild_id}")
        return result.fetchone()[0]
