# Changelog

All notable changes to this project will be documented in this file.

## [5.2.2] - 2024-04-07

### Added
- Added a new command `/suggestion retrieve_control_panel` to retrieve a control panel for a suggestion.
- Added a new command `/cases review` to review a case via a command.
- Added a new command `/level give_xp` to give XP to a user.
- Added a new command `/level remove_xp` to remove XP from a user.
- Added a new command `/level leaderboard` to view the leaderboard.
- Added a new command `/level show` to get an embed showing the user's level.
- Added a new dialogue option when closing a ticket to ask the staff member what category and subcategory the ticket should be closed under if one was not already selected.
- Added Join Alerts for when users join the server who have an existing moderation history.

### Changed
- Administrators can now review a Moderator Action taken by another Administrator.
- If a timeout is added using a method other than Sersi a timeout case will be created in Sersi.
- If a timeout is removed using a method other than Sersi the relevant timeout case will be closed in Sersi.
- If an Alert is deleted it will be reposted.
- If a suggestion is deleted it will be closed.
- If a vote embed is deleted it will be reposted.
- Replies now get bonus XP.
- If a ticket channel is deleted the ticket will be closed.
- Maybe votes increase the minimum time before a vote is decided.

### Fixed
- Fixed a bug where a closed ticket did not have the Close Reason displayed in the ticket closed embed or survey.
- Fixed a bug where "None" was displayed as the ranking parameter in the moderation leaderboard.