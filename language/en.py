# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks and Martijn Verlind                              #
# ------------------------------------------------------------------------- #

embed_footer="Info requested by: {member}. This dialog will show for {auto_delete_time} seconds."

# ------------------------------------------------------------------------- #
# SETTINGS #
# ------------------------------------------------------------------------- #
info_embed_title="Welcome to {bot_name}! {version}"
info_embed_description="{bot_name} for Discord"
info_embed_lang_field_name="Language"
info_embed_gmt_field_name="Timezone"
info_embed_auto_delete_field_name="Automatically delete Bot messages"
info_embed_auto_delete_field_value="seconds"
info_embed_raids_channel_field_name="Raids Channel"
info_embed_log_channel_field_name="Log Channel"
info_embed_moderator_role_field_name="Moderator Role"
info_embed_resources_field_name="Resources"
info_embed_resources_field_value_1="Invite {bot_name}"
info_embed_resources_field_value_2="Invite {bot_name}"
info_embed_resources_field_value_3="Discord Website"
info_embed_resources_field_value_4="Visit Discords website!"

updated_language="The language of this server is now set to `{language}`!"
updated_gmt="The timezone of this server is now set to `{gmt}`!"
updated_auto_delete_time="The auto delete time for this server is now set to `{seconds} seconds`!"
updated_raids_channel_changed="The raids channel for this server is now set to `{channel}`!"
updated_raids_channel_removed="The raids channel for this server is now `removed`!"
updated_logs_channel_changed="The logs channel for this server is now set to `{channel}`!"
updated_logs_channel_removed="The logs channel for this server is now `removed`!"
updated_moderator_role_changed="The moderator role for this server is now set to `{role}`!"

# ------------------------------------------------------------------------- #
# 2_location #
# ------------------------------------------------------------------------- #
create_success="I have successfully created the {location_type}!"
create_failed="Something went wrong while creating the {location_type}!"
delete_success="I have successfully deleted the {location_type}!"
delete_failed="Something went wrong while deleting the {location_type}!"
location_info_embed_location_does_not_exists="The `{location_type}` with the name `{location}` does not exist!"
location_info_embed_title="Location information"
location_info_embed_discription="Location: `{location}` -- Type: `{location_type}`."
location_info_google_maps="View location on Google Maps!"
location_info_embed_location_info_field_title="Location information:"
location_info_embed_location_info_field_value="Latitude: `{latitude}`\n Longitude: `{longitude}`"
location_info_embed_location_google_maps_field_title="Google Maps:"
location_info_embed_location_google_maps_field_value="[Go to google maps!]({link})"
location_info_paginate_embed_title="Locations list"
location_info_paginate_embed_description="List of all locations for this guild!"
location_info_paginate_embed_locations_title="Locations:"
location_info_paginate_embed_no_results="There are no `{location_type}'s` available in this server!"

# ------------------------------------------------------------------------- #
# 3_raids #
# ------------------------------------------------------------------------- #
raid_location_does_not_exist="There are no locations with the name: `{name}`!"
raid_invalid_time_format="The given time was in an invalid format, please use `HH:MM`!"
raid_invalid_date_format="The given date was in an invalid format, please use `DD-MM-YYYY`!"
raid_generated_id_duplicate="The generated idea already exists, please try again!"

raid_successfully_created="The `{raid_type}` is created!"
raid_embed_description="**Raid ID:** {raid_id}\n**Time:** {time}\n**Date:** {date}\n**Location:** [{location}](https://www.google.com/maps/@{latitude},{longitude},14z)\n**Type:** {raid_type}"
raid_embed_footer="Raid created by: {member} | Total attendees: {attendees}"

raid_unable_to_delete_not_creator_or_enough_permissions="You can't delete this raid because you didn't create it and you don't have the right permissions!"
raid_successfully_deleted="The raid with id: `{id}` successfully deleted!"

raid_unable_to_find="I didn't find the raid with ID: `{id}`!"
raid_unable_to_edit_not_creator_or_enough_permissions="You can't edit this raid because you didn't create it and you don't have the right permissions!"
raid_successfully_edited="The raid with id: `{id}` successfully edited!"

# ------------------------------------------------------------------------- #
# ERRORS #
# ------------------------------------------------------------------------- #
# General
error_command_in_development="The command: `{command}` is in development and will be added later. Your input: {input}!"
# Validate
error_latitude_invalid="I am sorry, the given `latitude` is invalid! Your input: `{latitude}`!"
error_longitude_invalid="I am sorry, the given `longitude` is invalid! Your input: `{longitude}`!"
# Pokemon
pokemon_not_found="I could not find `{pokemon}`!"

# ------------------------------------------------------------------------- #
# LOG CHANNEL RESPONSES #
# ------------------------------------------------------------------------- #
# 1_settings
log_channel_info_requested="`[{datetime}]` - **{member}** requested information about me!"
log_channel_language_changed="`[{datetime}]` - **{member}** changed the language for this server to `{language}`!"
log_channel_timezone_changed="`[{datetime}]` - **{member}** changed the timezone for this server to `{offset}`!"
log_channel_auto_delete_time_changed="`[{datetime}]` - **{member}** changed the auto delete time for this server to `{seconds} seconds`!"
log_channel_raids_channel_changed="`[{datetime}]` - **{member}** changed the raids channel for this server to `{channel}`!"
log_channel_log_channel_changed="`[{datetime}]` - **{member}** changed the log channel for this server to `{channel}`!"
log_channel_moderator_role_changed="`[{datetime}]` - **{member}** changed the moderator role for this server to `{role}`!"

# 2_location
log_channel_location_successfully_created="`[{datetime}]` - **{member}** successfully created a new `{location_type}` with the name: `{name}`!"
log_channel_location_creation_failed="`[{datetime}]` - **{member}** tried creating a new `{location_type}` with the name: `{name}` but the execution failed!"
log_channel_location_successfully_deleted="`[{datetime}]` - **{member}** successfully deleted a `{location_type}` with the name: `{name}`!"
log_channel_location_deletion_failed="`[{datetime}]` - **{member}** tried deleting a `{location_type}` with the name: `{name}` but the execution failed!"
log_channel_location_info_request="`[{datetime}]` - **{member}** requested information about one or more `{location_type}`!"

# 3_raid
log_channel_raid_successfully_created="`[{datetime}]` - **{member}** created a new `{raid_type}`!"
log_channel_raid_creation_failed="`[{datetime}]` - **{member}** tried creating a new `{raid_type}` but the execution failed!"
log_channel_raid_successfully_deleted="`[{datetime}]` - **{member}** deleted `{raid_type}` with id: `{id}`!"
log_channel_raid_deletion_failed="`[{datetime}]` - **{member}** tried deleting a `{raid_type}` but the execution failed!"
log_channel_raid_successfully_edited="`[{datetime}]` - **{member}** edited the `{raid_type}` with id: `{id}`!"
log_channel_raid_edit_failed="`[{datetime}]` - **{member}** tried editing a `{raid_type}` but the execution failed!"