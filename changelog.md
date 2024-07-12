# Changelog

All notable changes to this project will be documented in this file.

## [5.3.0] - 2024-06-??

### Added
- Added voice message text transcription feature
- Timers can now be cancelled via `/timer cancel` command
- WhoIs embed now includes the user's roles
- WhoIs embed now has a button to bring up the user's levelling embed
- Added MassPing detection
    - If a user tries to ping more than 6 users the user will be warned. Further attempts will result in a timeout.
- When a user leaves the server the bot will now store their roles and will restore them if they rejoin within 28 days
- Added a `/roles` top-level command
    - '/roles add_opt_in' - Allows you to make a role opt-in
    - '/roles remove_opt_in' - Removes the role from the opt-in list
    - '/roles edit_role' - Allows you to edit details about an opt-in role
    - '/roles add_category' - Allows you to create a category for opt-in roles
    - '/roles remove_category' - Allows you to remove a category
    - '/roles create_temporary_role' - Allows you to create a temporary role
    - '/roles unmake_temporary_role' - Removes the temporary role status from a role
    - '/roles give_temporary_role' - Adds a temporary role to a user
    - '/roles remove_temporary_role' - Removes a temporary role from a user
    - '/roles list_temporary_roles' - Lists all temporary roles
    - '/roles list_issued_temporary_roles' - Lists all temporary roles issued to a user

### Changed
- The bot will no longer send a message when a potential slur is declared a False Positive

### Fixed
- Fixed a bug where daily moderation statistics would not be sent after a change of month
- Fixed a bug where the bot would sometimes not be able to close a ticket
- Fixed a bug where a user who is timed out as part of a ban vote would trigger the "Timed Out by Non-Sersi" message