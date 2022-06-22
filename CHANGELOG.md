# VictreeBot Changelog
All notable changes will be documented in this file.
VictreeBot uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

================================================================

## [Unreleased/Working on]

================================================================

## [0.5.0] - 22-06-2022
### [NEW]
- Added function to update log settings ( **/settings update logging** )
- Added info command to view bot info
- Added pokedex command ( **/pokedex** )

## [0.4.2] - 20-06-2022
### [Bugfixes]
- Fix for translations
- Fix for raids not being loaded properly causing issues with adding and removing emoji's

## [0.4.1] - 20-06-2022
### [Bugfixes]
- Fix for trade message with components not getting deleted

## [0.4.0] - 20-06-2022
### [NEW]
- Added trading
    - Trade proposal
    - Trade offer
    - Trade search
### [Bugfixes]
- Updated constants

## [0.3.0] - 20-06-2022
### [NEW]
- Added raids
    - Added raid create
    - Added raid delete
    - Added raid edit
- Added bot activities
- Added the ability to change settings
### [Bugfixes]
- Fix log_locations_edit not being used/working properly
- Fix for multiple locations with "'" being allowed
### [Changes]
- Changes latitude/longitude questions order

## [0.2.3] - 16-06-2022
### [Bugfixes]
- Fix NotFoundError on reset
- Changes to Internal logging
### [Changes]
- Improved reset and setup commands
- Changed default role names
- Changed default emoji names
- Changes the welcome message format because of name changes

## [0.2.2] - 16-06-2022
### [Bugfixes]
- Fix for some location interactions not working
### [Changes]
- Added permissions check to setup and reset command (manage server permission now needed)
- Reset commands now deletes channels based on their ID instead of name

## [0.2.1] - 15-06-2022
### [Bugfixes]
- Fix bot not sending welcome message on join because of missing permissions

## [0.2.0] - 15-06-2022
### [NEW]
- Added location interactions (Gyms and Pokéstops)
    - Add location
    - Delete location
    - Edit location
    - List location
    - Info about location
- Added different events
    - guild_join_setup
    - guild_leave_remove
    - member_create_add
    - member_delete_remove
### [Bugfixes]
- Added avatar to profile view
### [Changes]
- Changed format of internal VictreeBot Logging

## [0.1.0] - 12-06-2022
### [NEW]
- Added profile editing
- Added profile viewing

## [0.0.0] - 16-05-2022
Initial start and setup of the new and improved VicreeBot project.
