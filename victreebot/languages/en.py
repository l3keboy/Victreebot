# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
validate_enable_or_disable = "Enable or disable {item}"
validate_enable_or_disable_description = "Do you want to enable or disable {item}?"
disable = "Disable"
enable = "Enable"
enable_disable_timeout = "Enable or disable validation reached a timeout! Returning disable"
validate_add_or_no_add = "Add {item}"
validate_add_or_no_add_description = "Do you want to add {item}?"
no = "No"
yes = "Yes"
add_no_add_timeout = "Add or don't add validation reached a timeout! Returning don't add"

# ------------------------------------------------------------------------- #
# EVENTS #
# ------------------------------------------------------------------------- #

# ------------------------------------------------------------------------- #
# INTERACTIONS #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# setup #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# setup.py #
# ------------------------------------------------------------------------- #
# Responses
response_already_setup = "{bot_name} is already setup!"
response_not_yet_setup = "{bot_name} is not yet setup! Please contact the administrator of the server to setup {bot_name}!"
# Log responses
# Embeds
setup_started_embed_title = "{bot_name} setup started!"
setup_started_embed_description = "Please wait while {bot_name} gets things ready!"
setup_finished_embed_title = "{bot_name} setup finished!"
setup_finished_embed_description = "{bot_name} is finished with the setup! Please check {logs_channel_mention} for extra info!"

# ------------------------------------------------------------------------- #
# reset.py #
# ------------------------------------------------------------------------- #
# Responses
response_reset_timeout_reached = "Reset request reached a timeout! Not resetting!"
response_reset_cancelled = "Reset cancelled! Not resetting {bot_name}!"
response_reset_from_channel_not_possible = "You can't reset from this channel!"
# Log responses
log_response_reset_timeout_reached = "`[{datetime}]` -- **{member}** tried to reset {bot_name}, but the timeout was reached!"
log_response_reset_cancelled = "`[{datetime}]` -- **{member}** tried to reset {bot_name}, but they cancelled the request!"
# Embeds
reset_validation_embed_title = "{bot_name} reset requested!"
reset_validation_embed_description = "Are you sure you want to reset {bot_name}?\n This will reset:\n - {bot_name} emoji's\n - {bot_name} channels\n - {bot_name} roles\n - Removed ongoing raids\n\n This will not reset:\n - {bot_name} language\n - {bot_name} auto_delete\n - {bot_name} GMT\n - {bot_name} Unit System\n - {bot_name} log variables\n - User profiles\n - {bot_name} locations\n"
reset_started_embed_title = "{bot_name} reset started!"
reset_started_embed_description = "Please wait while {bot_name} resets all values!"
reset_finished_embed_title = "{bot_name} is reset!"
reset_finished_embed_description = "{bot_name} has been reset! You can now use `/setup` again!"


# ------------------------------------------------------------------------- #
# profile #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# edit.py #
# ------------------------------------------------------------------------- #
profile_action_row_add_friend_code = "Add friend code(s)"
profile_modal_add_friend_codes = "Add friend code(s)"
profile_modal_add_friend_codes_text_input_title = "Which friend code(s) do you want to add?"
profile_modal_add_friend_codes_text_input_placeholder = (
    "1234 5678 9012 or 1234-5678-9012 (Note: If adding multiple friend codes, please seperate with a ,)"
)
profile_action_row_delete_friend_code = "Delete friend code(s)"
profile_modal_delete_friend_codes = "Delete friend code(s)"
profile_modal_delete_friend_codes_text_input_title = "Which friend code(s) do you want to delete?"
profile_modal_delete_friend_codes_text_input_placeholder = (
    "1234-5678-9012 (Note: If deleting multiple friend codes, please seperate with a ,)"
)
profile_action_row_add_active_location = "Add active location(s)"
profile_modal_add_active_locations = "Add active location(s)"
profile_modal_add_active_locations_text_input_title = "Which location(s) do you want to add?"
profile_modal_add_active_locations_text_input_placeholder = (
    "New York (Note: If adding multiple locations, please seperate with a ,)"
)
profile_action_row_delete_active_location = "Delete active location(s)"
profile_modal_delete_active_locations = "Delete active location(s)"
profile_modal_delete_active_locations_text_input_title = "Which location(s) do you want to delete?"
profile_modal_delete_active_locations_text_input_placeholder = (
    "New York (Note: If deleting multiple locations, please seperate with a ,)"
)
# Response
response_profile_edit_timeout_reached = "Stopping profile editing, timeout reached!"
response_profile_edit_success = "Your account has been edited!"
# Log response
log_response_profile_edit_timeout_reached = (
    "`[{datetime}]` -- **{member}** tried to edit their profile, but the timeout was reached!"
)
log_response_profile_edit = "`[{datetime}]` -- **{member}** edited their profile!"
# Embeds
profile_edit_embed_title = "Profile configuration"
profile_edit_embed_description = "Welcome to the profile configurator. Please select what action you want to perform."

# ------------------------------------------------------------------------- #
# view.py #
# ------------------------------------------------------------------------- #
profile_no_friend_codes_set = "No friend codes set!"
profile_no_active_locations_set = "No active locations set!"
# Response
# Log response
log_response_profile_view = "`[{datetime}]` -- **{member}** viewed {target_member} their profile!"
# Embeds
profile_view_embed_title = "Profile"
profile_view_embed_description = "Viewing {member}'s profile"
profile_view_embed_field_friend_codes = "Friend codes:"
profile_view_embed_field_active_locations = "Active in:"
profile_view_embed_field_raids_created = "Created"
profile_view_embed_field_raids_participated = "Participated in"


# ------------------------------------------------------------------------- #
# locations #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# locations.py #
# ------------------------------------------------------------------------- #
location_action_row_list_gym = "List all gym's"
location_action_row_list_pokestop = "List all pokéstops"
location_action_row_info_gym = "Get info about a gym"
location_action_row_info_pokestop = "Get info about a pokéstop"
location_action_row_add_gym = "Add gym"
location_action_row_delete_gym = "Delete gym"
location_action_row_edit_gym = "Edit gym"
location_action_row_add_pokestop = "Add pokéstop"
location_action_row_delete_pokestop = "Delete pokéstop"
location_action_row_edit_pokestop = "Edit pokéstop"
location_action_row_edit_description = "Edit description"
location_action_row_edit_latitude_longitude = "Edit latitude and longitude"
location_name_modal_location_name = "{location} name"
location_name_modal_text_input_title = "What is the name of the {location}?"
location_name_modal_text_input_placeholder = "New York"
location_longitude_latitude_modal_location_name = "{location} longitude and latitude"
location_longitude_modal_text_input_title = "{location} longitude"
location_longitude_modal_text_input_placeholder = "What is the longitude?"
location_latitude_modal_text_input_title = "{location} latitude"
location_latitude_modal_text_input_placeholder = "What is the latitude?"
location_description_modal_location_name = "{location} description"
location_description_modal_text_input_title = "{location} description"
location_description_modal_text_input_placeholder = "What is the description?"
location_google_maps = "View in Google Maps!"
location_no_coordinates_set = "No coordinates set!"
location_no_description_set = "This location doesn't have a description!"
# Response
response_location_interactions_timeout_reached = "Stopping location interaction, timeout reached!"
response_location_invalid_latitude_longitude = "The given latitude or longitude is invalid!"
response_location_add_failed_already_exists = "A `{location_type}` with that name already exists!"
response_location_add_failed = (
    "Something went wrong while trying to add the location! Does this location already exist?"
)
response_location_add_success = "The location has been added!"
response_location_delete_failed = "Something went wrong while trying to delete the location!"
response_location_delete_success = "The location has been deleted!"
response_location_edit_failed = "Something went wrong while trying to edit the location!"
response_location_edit_success = "The location has been edited!"
response_location_delete_failed_no_such_location = "No `{location_type}` with that name found!"
response_location_edit_failed_no_such_location = "No `{location_type}` with that name found!"
response_location_list_no_results = "There are no `{location_type}'s` in this server!"
response_location_info_no_results = "There is no `{location_type}` with that name!"
# Log response
log_response_location_interactions_timeout_reached = (
    "`[{datetime}]` -- **{member}** tried to interact with locations, but the timeout was reached!"
)
log_response_location_invalid_latitude_longitude = (
    "`[{datetime}]` -- **{member}** tried to add a {location_type}, but the given latitude or longitude is not correct!"
)
log_response_location_add_failed_already_exists = "`[{datetime}]` -- **{member}** tried to add a `{location_type}`, but a `{location_type}` with the specified name already exists!"
log_response_location_add_failed = "`[{datetime}]` -- **{member}** tried to add a location, but something went wrong!"
log_response_location_add_success = "`[{datetime}]` -- **{member}** added a location!"
log_response_location_delete_failed = (
    "`[{datetime}]` -- **{member}** tried to delete a location, but something went wrong!"
)
log_response_location_delete_success = "`[{datetime}]` -- **{member}** deleted a location!"
log_response_location_edit_failed = "`[{datetime}]` -- **{member}** tried to edit a location, but something went wrong!"
log_response_location_edit_success = "`[{datetime}]` -- **{member}** edited a location!"
log_response_location_delete_failed_no_such_location = "`[{datetime}]` -- **{member}** tried to delete a `{location_type}`, but there was no `{location_type}` with the specified name!"
log_response_location_edit_failed_no_such_location = "`[{datetime}]` -- **{member}** tried to edit a `{location_type}`, but there was no `{location_type}` with the specified name!"
log_response_location_list_no_results = "`[{datetime}]` -- **{member}** tried to list `{location_type}'s`, but there are no `{location_type}'s` in this server!"
log_response_location_list_requested = "`[{datetime}]` -- **{member}** requested the list of `{location_type}'s`!"
log_response_location_info_no_results = "`[{datetime}]` -- **{member}** requested information about a `{location_type}'s`, but the given name does not exist!"
log_response_location_info_requested = (
    "`[{datetime}]` -- **{member}** requested information about a `{location_type}'s`!"
)
# Embeds
location_embed_title = "Location view"
location_embed_description = "Welcome to the location view. Please select what action you want to perform."
location_list_embed_title = "Location list"
location_list_embed_description = "Showing all `{location_type}'s`!"
location_list_embed_field_locations = "Locations:"
location_info_embed_title = "Location info"
location_info_embed_field_coordinates = "Coordinates:"
location_info_embed_field_google_maps = "Google Maps link:"
