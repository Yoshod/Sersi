# Changelog

All notable changes to this project will be documented in this file.

## [5.2.2] - YYYY-MM-DD

### Added
- Added a new command `/suggestion retrieve_control_panel` to retrieve a control panel for a suggestion.
- Added a new command `/cases review` to review a case via a command.

### Changed
- Administrators can now review a Moderator Action taken by another Administrator.
- If a timeout is added using a method other than Sersi a timeout case will be created in Sersi.
- If a timeout is removed using a method other than Sersi the relevant timeout case will be closed in Sersi.
- If an Alert is deleted it will be reposted.
- If a suggestion is deleted it will be closed.
- If a vote embed is deleted it will be reposted.

### Fixed
- Fixed a bug where a closed ticket did not have the Close Reason displayed in the ticket closed embed or survey.
- Fixed a bug where "None" was displayed as the ranking parameter in the moderation leaderboard.