# Changelog

All notable changes to this project will be documented in this file.

## [5.2.3] - 2024-04-??

### Added
- Added a Starboard to the bot.
    - When a post gets a minimum amount of stars it will be posted to the starboard.
    - When a post goes below a minimum amount of stars it will be removed from the starboard.
    - A post can be starred either from the post itself or the starboard. This is checked for duplicates.
- Added a command `\starboard` to manage the starboard.
    - `ignore` - Ignore a channel from the starboard.
    - `unignore` - Unignore a channel from the starboard.
- Added a feedback system to the bot.
    - When feedback is received it will be sent to either a feature request or bug report channel in the development server.
    - These can be responded by the developers.
    - They can Approved which will automatically create a feature request or bug report on the GitHub repository.
    - They can Denied which will close the feedback.
    - A user can be banned from sending feedback.
- Added a command `\feedback` to give feedback to the bot.
    - `bug_report` - Report a bug.
    - `feature_request` - Request a feature.


### Changed

### Fixed
