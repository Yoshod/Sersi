import sqlite3


# SQLite3 powered data storage, used to store all randomly accessible data.
class Database:
    # Loads in the database, with the given absolute path.
    def __init__(self, path):
        self.connection = sqlite3.connect(path)

        # TODO: set up database if it doesn't hold the tables we need

    # Commits all outstanding changes.
    def commit_changes(self):
        self.connection.commit()

    # TODO: implement modification methods
