# VictreeBot Changelog

All notable changes will be documented in this file.
VictreeBot uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

================================================================

## [Unreleased/Working on]

================================================================

## [0.9.1] - 31-10-2024

### [Bugfixes]

- Fixed an issue with a local path not being found in the docker container causing some commands to fail.
- Added a temp try, except block to improve debugging for an unknown issue occuring in the PROD docker image

## [0.9.0] - 21-10-2024

### [BREAKING]

- Remove automatic updating based on GitHub repository.
- Migrated to Docker image.

### [NEW]

- Added files for building docker image
- Added pipelines for automatic building of image and deploying to https://hub.docker.com/.

## [0.8.0] - 10-03-2024

### [NEW]

- Add Shadow raid option in raid create command
- Add Shadow egg option in raid create command

### [Changes]

- Egg icon in raid embed now only shows as an image and not in the author portion of the embed

### [Bugfixes]

- Fix the `/setup` command not working
- Fix the `/reset` command not working

## [0.7.14] - 28-10-2023

### [Bugfixes]

- Fix for raids not working correctly when using an unknown location

## [0.7.13] - 11-05-2023

### [Bugfixes]

- Fix for old boss images staying when changing boss

## [0.7.12] - 22-04-2023

### [Bugfixes]

- Fix for locations not working correctly

## [0.7.11] - 12-04-2023

### [Bugfixes]

- Fix for some commands not working after bumping dependencies

## [0.7.10] - 10-04-2023

### [BREAKING]

- Bump different dependencies

## [0.7.9] - 02-11-2023

### [Bugfixes]

- Fix action rows with new dependency update

## [0.7.8] - 25-01-2022

### [Bugfixes]

- Fix for listing locations not working

## [0.7.7] - 24-01-2022

### [Bugfixes]

- Extra fix for message buttons not showing because of dependency upgrades

## [0.7.6] - 03-01-2022

### [BREAKING]

- Bump different dependencies

### [Bugfixes]

- Fix for message buttons not showing because of dependency upgrades

## [0.7.5] - 11-11-2022

### [Bugfixes]

- Fixed an issue where reactions where not responding correctly

## [0.7.4] - 05-11-2022

### [Bugfixes]

- Fixed an issue where raids can not be deleted by the moderator

## [0.7.3] - 05-11-2022

### [Bugfixes]

- Fixed an issue where raids can not be edited by the moderator

## [0.7.2] - 15-10-2022

### [NEW]

- Added support for Elite-Raids
- EX-Raids support is also back
- Added change date and time functionality to /raid_edit

## [0.7.1] - 17-09-2022

### [Bugfixes]

- Fixed an issue where locations with the character, ', couldn't be used in a raid (Issue ID: #87)

## [0.7.0] - 11-09-2022

### [NEW]

- Added 4 custom bosses: Egg1, Egg3, Egg5 and EggMega! (Issue ID: #81)

### [Bugfixes]

- Added bigger thumbnail to raid embed (Issue ID: #84)
- Fixed an issue where the wrong month would be shown on the raid create command (Issue ID: #85)

## [0.6.1] - 04-09-2022

### [NEW]

- Added server setting for extended time format

### [Bugfixes]

- Fixed an issue where locations list was not displayed properly
- Removed EX-Raids from raid create options since this is not being used anymore by Pokemon Go
- Fixed an issue where the raid location didn't have spaces
- Fixed an issue where the raid location didn't have a clickable link

## [0.6.0] - 04-09-2022

### [NEW]

- Implemented autocomplete
- /locations command is now split into /locations and /locations_info

### [BREAKING]

- /raid create: command working changed due to implementation of autocomplete (added boss and location parameters which support autocomplete)
- /raid edit: command working changed due to implementation of autocomplete (raid_id parameter is now autocompleted, added new_boss, new_location and new_raid_type parameters which support autocomplete)
- /raid delete: command working changed due to implementation of autocomplete (raid_id parameter is now autocompleted)
- /trade: command working changed due to implementation of autocomplete (now to optional parameters (Tip: combine them to create a proposal))
- /locations_info: command added with location parameter to support autocomplete
- /pokedex: boss parameter now supports autocomplete

### [Bugfixes]

- Fixed an issue where the info command wouldn't show the correct auto delete time

## [0.5.3] - 02-09-2022

### [Bugfixes]

- Fix for modals not working

## [0.5.2] - 02-09-2022

### [Bugfixes]

- Fix startup
- Update requirements.txt
- Update .gitignore

## [0.5.1] - 22-06-2022

### [Bugfixes]

- Fix for info command requiring manage server permissions
- Fix for info and pokedex embed not being in the right color

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
