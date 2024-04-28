# Changelog

All notable changes to this project will be documented in this file.

## [5.2.3] - 2024-04-??

### Added
- Added new xp types (community, event, moderation)
- Having suggestion approved and voted on and implemented awards the suggester xp, voting on suggestions also awards xp
- Added a Starboard to the bot.
    - When a post gets a minimum amount of stars it will be posted to the starboard.
    - When a post goes below a minimum amount of stars it will be removed from the starboard.
    - A post can be starred either from the post itself or the starboard. This is checked for duplicates.
    - Members with posts on the starboard receive xp for each star
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
- Added a Welcome DM system.
    - When a user joins the server they will receive a DM from the bot.
    - This DM will have different contents depending on whether:
        - The user has joined the server for the first time.
        - The user has joined the server before.
        - The user has joined the server before and is timedout.
- Added a feature where if there are any potential tracking strings in a URL the bot will reply (non-ping) with the cleaned URL.
- Polls now contain a pie chart

### Changed
- Suggestions are now automatically upvoted by the suggester
- Multiple choices polls now display % of people who picked a given option
- Reformation inamates are no longer allowed to be a reformist at the same time
    - reformist role is removed upon when sent to reformation
    - can no longer opt-in to the reformist role while in reformation

### Fixed
- Fixed a bug where users with previous expired timeout cases would still strigger "Timed Out User Left" alerts
- Fixed a bug where trying to remove a timeout using an invalid case ID would cause the bot to error
