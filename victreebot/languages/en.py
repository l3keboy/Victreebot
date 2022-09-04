monday = "Monday"
tuesday = "Tuesday"
wednesday = "Wednesday"
thursday = "Thursday"
friday = "Friday"
saturday = "Saturday"
sunday = "Sunday"
weekdays = [monday, tuesday, wednesday, thursday, friday, saturday, sunday]
january = "January"
february = "February"
march = "March"
april = "April"
may = "May"
june = "June"
july = "July"
august = "August"
september = "September"
october = "October"
november = "November"
december = "December"
months = [january, february, march, april, may, june, july, august, september, october, november, december]

validate_enable_or_disable = "Enable or disable {item}"
validate_enable_or_disable_description = "Do you want to enable or disable {item}?"
disable = "Disable"
disabled = "Disabled"
enable = "Enable"
enabled = "Enabled"
enable_disable_timeout = "Enable or disable validation reached a timeout! Returning disable"
validate_add_or_no_add = "Add {item}"
validate_add_or_no_add_description = "Do you want to add {item}?"
no = "No"
yes = "Yes"
add_no_add_timeout = "Add or don't add validation reached a timeout! Returning don't add"

error_response_not_enough_permissions_for_channel = "I do not have enough permissions to use this channel!"
error_response_not_a_text_channel = "The given channel is not a text channel!"
error_response_invalid_int_found = (
    "Oops! It looks like that a value or one of the values is not a valid integer/number!"
)

log_errors = "Errors"
log_info = "Info requests"
log_settings_changed = "Changed to settings"
log_profile_edit = "Profile edits"
log_profile_view = "Profile views"
log_location_add = "Location adds"
log_location_delete = "Location deletions"
log_location_edit = "Location edits"
log_location_info = "Location info requests"
log_location_list = "Location listings"
log_raid_create = "Raid creations"
log_raid_edit = "Raid edits"
log_raid_delete = "Raid deletions"
log_trade_offer = "Trade offers"
log_trade_proposal = "Trade proposals"
log_trade_search = "Trade searches"

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
response_not_yet_setup = (
    "{bot_name} is not yet setup! Please contact the administrator of the server to setup {bot_name}!"
)
# Log responses
# Embeds
setup_started_embed_title = "{bot_name} setup started!"
setup_started_embed_description = "Please wait while {bot_name} gets things ready!"
setup_finished_embed_title = "{bot_name} setup finished!"
setup_finished_embed_description = (
    "{bot_name} is finished with the setup! Please check {logs_channel_mention} for extra info!"
)

# ------------------------------------------------------------------------- #
# reset.py #
# ------------------------------------------------------------------------- #
# Responses
response_reset_timeout_reached = "Reset request reached a timeout! Not resetting!"
response_reset_cancelled = "Reset cancelled! Not resetting {bot_name}!"
response_reset_from_channel_not_possible = "You can't reset from this channel!"
# Log responses
log_response_reset_timeout_reached = (
    "`[{datetime}]` -- **{member}** tried to reset {bot_name}, but the timeout was reached!"
)
log_response_reset_cancelled = (
    "`[{datetime}]` -- **{member}** tried to reset {bot_name}, but they cancelled the request!"
)
# Embeds
reset_validation_embed_title = "{bot_name} reset requested!"
reset_validation_embed_description = "Are you sure you want to reset {bot_name}?\n This will reset:\n - {bot_name} emoji's\n - {bot_name} channels\n - {bot_name} roles\n - Removed ongoing raids\n\n This will not reset:\n - {bot_name} language\n - {bot_name} auto_delete\n - {bot_name} GMT\n - {bot_name} Unit System\n - {bot_name} log variables\n - User profiles\n - {bot_name} locations\n"
reset_started_embed_title = "{bot_name} reset started!"
reset_started_embed_description = "Please wait while {bot_name} resets all values!"
reset_finished_embed_title = "{bot_name} is reset!"
reset_finished_embed_description = "{bot_name} has been reset! You can now use `/setup` again!"


# ------------------------------------------------------------------------- #
# pokedex #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# pokedex.py #
# ------------------------------------------------------------------------- #
height_metric_system = "meters"
height_imperial_system = "foot"
height_usc_system = "inches"
weight_metric_system = "kilograms"
weight_imperial_system = "pounds"
weight_usc_system = "pounds"
# Response
response_pokedex_unknown_pokemon = "The pokémon `{boss_name}` does not seem to exist!"
# Log response
log_response_pokedex_unknown_pokemon = "`[{datetime}]` -- **{member}** requested information about a pokémon, but the given pokémon does not seem to exist!"
log_response_pokedex_requested = "`[{datetime}]` -- **{member}** requested the pokédex of a pokémon!"
# Embeds
pokedex_embed_title = "Pokédex information about {pokemon}"
pokedex_embed_name_title = "Pokémon name:"
pokedex_embed_id_title = "Pokémon ID:"
pokedex_embed_length_weight_title = "Pokémon height and weight:"
pokedex_embed_abilities_title = "Abilities:"

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
response_profile_edit_invalid_friend_code_format = "The given friend code is not in the correct format!"
# Log response
log_response_profile_edit_timeout_reached = (
    "`[{datetime}]` -- **{member}** tried to edit their profile, but the timeout was reached!"
)
log_response_profile_edit = "`[{datetime}]` -- **{member}** edited their profile!"
log_response_profile_edit_invalid_friend_code_format = "`[{datetime}]` -- **{member}** tried to edit their friend code(s), but the given friend code(s) is not in the correct format!"
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
response_location_info_no_results = "There is no location with that name!"
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
log_response_location_info_no_results = (
    "`[{datetime}]` -- **{member}** requested information about a location, but the given name does not exist!"
)
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


# ------------------------------------------------------------------------- #
# Raids #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# create.py #
# ------------------------------------------------------------------------- #
raid_create_modal_time = "Raid time"
raid_create_modal_time_text_input = "At what time?"
raid_create_modal_time_text_input_placeholder = "Format: HH:MM"
boss_name_modal_location_name = "Raid Boss"
boss_name_modal_text_input_title = "Boss name or ID"
boss_name_modal_text_input_placeholder = "What is the name or ID of the boss?"
# Responses
response_raid_create_timeout_reached = "Stopping Raid creation, timeout was reached!"
response_raid_create_location_not_found = (
    "The `{location_type}` with the name `{location_name}` does not exist! Please try to create the Raid again!"
)
response_raid_create_unknown_boss = "The given boss, `{boss_name}`, is not found! Please try to create the Raid again!"
response_raid_create_invalid_time = "The given time is not in a valid timeformat!"
response_raid_create_date_time_already_past = "The given date and time combination is in the past!"
response_raid_create_success = "The raid is created!"
# Log responses
log_response_raid_create_timeout_reached = (
    "`[{datetime}]` -- **{member}** tried to create a raid, but the timeout was reached!"
)
log_response_raid_create_location_not_found = (
    "`[{datetime}]` -- **{member}** tried to create a raid, but the given location does not exist!"
)
log_response_raid_create_unknown_boss = (
    "`[{datetime}]` -- **{member}** tried to create a raid, but the given boss is not found!"
)
log_response_raid_create_invalid_time = (
    "`[{datetime}]` -- **{member}** tried to create a raid, but the given time is not in the valid format!"
)
log_response_raid_create_date_time_already_past = (
    "`[{datetime}]` -- **{member}** tried to create a raid, but the given date and time combination is in the past!"
)
log_response_raid_create_success = "`[{datetime}]` -- **{member}** created a raid!"
# Embed
raid_create_embed_title_raid_type = "Raid type"
raid_create_embed_description_raid_type = "Please select the type of the raid."
raid_create_embed_title_location_type = "Location type"
raid_create_embed_description_location_type = "Please select the type of the location where the raid takes place."
raid_create_embed_title_date = "Raid date and time"
raid_create_embed_description_date = "When does the raid take place? (Note: The format of the dates is: Month/Day!)"
raid_embed_description_with_location_link = "**Raid ID:** {raid_id}\n **Raid type:** {raid_type}\n **Time and date:** {time_date}\n **Location:** [{location}](https://www.google.com/maps/place/{latitude},{longitude})\n"
raid_embed_description_without_location_link = (
    "**Raid ID:** {raid_id}\n **Raid type:** {raid_type}\n **Time and date:** {time_date}\n **Location:** {location}\n"
)
raid_embed_footer = "Raid created by: {member} | Total attendees: {attendees}"

# ------------------------------------------------------------------------- #
# delete.py #
# ------------------------------------------------------------------------- #
# Response
response_raid_delete_no_raid_found = "I didn't find a raid with that ID!"
response_raid_delete_not_creator_or_moderator = (
    "You are not allowed to delete this raid! You are not the owner or a {bot_name} moderator!"
)
response_raid_delete_success = "The raid is deleted!"
# Log response
log_response_raid_delete_no_raid_found = (
    "`[{datetime}]` -- **{member}** tried to delete a raid, but didn't there was no raid with the given ID!"
)
log_response_raid_delete_not_creator_or_moderator = (
    "`[{datetime}]` -- **{member}** tried to delete a raid, but they aren't the creator or a {bot_name} moderator!"
)
log_response_raid_delete_success = "`[{datetime}]` -- **{member}** deleted a raid!"
# Embed

# ------------------------------------------------------------------------- #
# edit.py #
# ------------------------------------------------------------------------- #
raid_edit_action_row_edit_raid_type = "Raid type"
raid_edit_action_row_edit_boss = "Boss"
raid_edit_action_row_edit_location = "Location"
raid_edit_action_row_edit_date_time = "Date and time"
# Response
response_raid_edit_no_raid_found = "There is no raid with that ID!"
response_raid_edit_not_creator_or_moderator = (
    "You are not allowed to edit this raid! You are not the owner or a {bot_name} moderator!"
)
response_raid_edit_unknown_boss = "The given boss, `{boss_name}`, is not found! Please try to edit the Raid again!"
response_raid_edit = "The raid is edited!"
response_raid_edit_failed = "Something went wrong while editing the raid!"
response_raid_edit_timeout_reached = "Stopping Raid edit, timeout was reached!"
# Log response
log_response_raid_edit_no_raid_found = (
    "`[{datetime}]` -- **{member}** tried to edit a raid, but didn't there was no raid with the given ID!"
)
log_response_raid_edit_not_creator_or_moderator = (
    "`[{datetime}]` -- **{member}** tried to edit a raid, but they aren't the creator or a {bot_name} moderator!"
)
log_response_raid_edit_unknown_boss = (
    "`[{datetime}]` -- **{member}** tried to edit a raid, but the new boss isn't found!"
)
log_response_raid_edit_timeout_reached = (
    "`[{datetime}]` -- **{member}** tried to edit a raid, but the timeout was reached!"
)
log_response_raid_edit = "`[{datetime}]` -- **{member}** edited a raid!"
log_response_raid_edit_failed = "`[{datetime}]` -- **{member}** tried to edit a raid, but something went wrong!"

# Embed
raid_edit_embed_title = "Raid edit"
raid_edit_embed_description = "Please select the component of the raid you want to edit."
raid_edit_embed_title_location_type = "Location type"
raid_edit_embed_description_location_type = "Please select the type of the location where the raid takes place."


# ------------------------------------------------------------------------- #
# Settings #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# info.py #
# ------------------------------------------------------------------------- #
# Response
# Log response
log_response_info_requested = "`[{datetime}]` -- **{member}** requested my information!"
# Embeds
info_bot_embed_title = "{bot_name} info! {version}"
info_bot_embed_footer = "Server stats -- Raids completed: {raids_completed} | Raids created: {raids_created} | Raids deleted: {raids_deleted}"
info_bot_embed_field_title_language = "Language:"
info_bot_embed_field_title_auto_delete = "Auto delete:"
info_bot_embed_field_title_unit_system = "Unit system:"
info_bot_embed_field_title_gmt = "Timezone:"
info_bot_embed_field_title_timeout = "Raid timeout:"
info_bot_embed_field_title_instinct_emoji = "Instinct emoji:"
info_bot_embed_field_title_instinct_role = "Insstinct role:"
info_bot_embed_field_title_mystic_emoji = "Mystic emoji:"
info_bot_embed_field_title_mystic_role = "Mystic role:"
info_bot_embed_field_title_valor_emoji = "Valor emoji:"
info_bot_embed_field_title_valor_role = "Valor role:"
info_bot_embed_field_title_raids_channel = "Raids channel:"
info_bot_embed_field_title_logging_channel = "Logs channel:"
info_bot_embed_field_title_moderator_role = "Moderator role:"
info_bot_embed_field_title_logging_events_1 = "Logged events:"

# ------------------------------------------------------------------------- #
# settings_update.py #
# ------------------------------------------------------------------------- #
# Response
error_response_settings_update_insert_at_least_1 = "At least one setting change is required!"
response_settings_update_general_failed = "Something went wrong while trying to update `General Settings`!"
response_settings_update_general_success = "The `General Settings` are updated!"
response_settings_update_raid_failed = "Something went wrong while trying to update `Raid Settings`!"
response_settings_update_raid_success = "The `Raid Settings` are updated!"
response_settings_update_raid_failed_raids_active = (
    "Can't update `Raid Settings` because there are raids active in this server!"
)
# Log response
log_response_settings_update_general_failed = (
    "`[{datetime}]` -- **{member}** tried to edit `General Settings`, but something went wrong!"
)
log_response_settings_update_general_success = "`[{datetime}]` -- **{member}** edited `General Settings`!"
log_response_settings_update_raid_failed = (
    "`[{datetime}]` -- **{member}** tried to edit `Raid Settings`, but something went wrong!"
)
log_response_settings_update_raid_success = "`[{datetime}]` -- **{member}** edited `Raid Settings`!"
log_response_settings_update_raid_failed_raids_active = "`[{datetime}]` -- **{member}** tried to edit `Raid Settings`, but these are not editable now because there are raids active!"
# Embeds

# ------------------------------------------------------------------------- #
# settings_logging_update.py #
# ------------------------------------------------------------------------- #
settings_logging_logs_channel = "Logs channel"
settings_logging_general_events = "General events"
settings_logging_profile_events = "Profile events"
settings_logging_location_events = "Location events"
settings_logging_raid_events = "Raid events"
settings_logging_trade_events = "Trade events"
# Response
error_response_settings_update_logging_events_nothing_to_change = "There are no settings to `{status}`!"
error_response_settings_update_logging_events_user_input_longer_than_possible_events = (
    "You gave more values than possible, please try again by re-running the command!"
)
response_settings_update_logging_failed_timeout = "Stopping updates to logging settings, timeout reached!"
response_settings_update_logging_logs_channel_failed = "Something went wrong while trying to update the logs channel!"
response_settings_update_logging_logs_channel_success = "I have updated the logs channel to {channel}!"
response_settings_update_logging_events_failed = "Something went wrong while trying to update the `{event}`!"
response_settings_update_logging_events_success = "The `{event}` are updated!"
# Log response
log_response_settings_update_logging_failed_timeout = (
    "`[{datetime}]` -- **{member}** tried to edit `Logging Settings`, but the timeout was reached!"
)
log_response_settings_update_logging_logs_channel_failed_not_enough_privileges = "`[{datetime}]` -- **{member}** tried to edit the logs channel of the `Logging Settings`, but inserted a channel where I don't have enough permissions for!"
log_response_settings_update_logging_logs_channel_failed_not_a_text_channel = "`[{datetime}]` -- **{member}** tried to edit the logs channel of the `Logging Settings`, but didn't insert a text channel!"
log_response_settings_update_logging_logs_channel_failed = (
    "`[{datetime}]` -- **{member}** tried to edit the logs channel of the `Logging Settings`, but something went wrong!"
)
log_response_settings_update_logging_logs_channel_success = (
    "`[{datetime}]` -- **{member}** changed the logs channel to {channel}!"
)
log_response_settings_update_logging_events_failed = (
    "`[{datetime}]` -- **{member}** tried to change the {event}, but something went wrong!"
)
log_response_settings_update_logging_events_success = "`[{datetime}]` -- **{member}** changed the {event}!"
# Embeds
settings_update_logging_embed_title = "Update logging settings"
settings_update_logging_embed_description = "Please select what option you want to update."
settings_update_logging_embed_logs_channel_title = "Update logs channel"
settings_update_logging_embed_logs_channel_description = (
    "Please tag the channel which you want to use as the new logs channel or insert its ID."
)
settings_update_logging_embed_events_title = "Update events"
settings_update_logging_embed_events_description = "Please select the events you want to {status}"
settings_update_logging_embed_field_events = "Events that can be {status}:"


# ------------------------------------------------------------------------- #
# Trade #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# trade.py #
# ------------------------------------------------------------------------- #
boss_name_modal_trade = "Trading"
trade_action_row_proposal = "Make a trade proposal"
trade_action_row_offer = "Offer a Pokémon"
trade_action_row_search = "Search for a Pokémon"
pokemon_offer_name_modal_text_input_title = "Pokémon to offer"
pokemon_offer_modal_text_input_placeholder = "Which pokémon do you offer to trade?"
pokemon_search_modal_text_input_title = "Wanted pokémon"
pokemon_search_modal_text_input_placeholder = "Which pokémon are you looking for?"
# Response
response_trade_insert_at_least_one = "You must insert at least one Pokémon!"


response_trade_interactions_timeout_reached = "Stopping trade interaction, timeout reached"
response_trade_offer_unknown_pokemon_offer = (
    "The given pokemon to offer, `{boss_name}`, is not found! Please try to create the offer again!"
)
response_trade_offer_unknown_pokemon_search = (
    "The given pokemon to search for, `{boss_name}`, is not found! Please try to create the offer again!"
)
response_trade_proposal_member_proposing = "{member} created a trade proposal!"
response_trade_offer_member_offering = "{member} offered a pokémon!"
response_trade_search_member_searching = "{member} is searching for a pokémon!"
# Log response
log_response_trade_insert_at_least_one = "`[{datetime}]` -- **{member}** tried to trade, but didn't insert a Poke!"


log_response_trade_interactions_timeout_reached = (
    "`[{datetime}]` -- **{member}** tried to trade, but the timeout was reached!"
)
log_response_trade_offer_unknown_pokemon_offer = (
    "`[{datetime}]` -- **{member}** tried to propose a trade, but the given pokémon to offer is not found!"
)
log_response_trade_offer_unknown_pokemon_search = (
    "`[{datetime}]` -- **{member}** tried to propose a trade, but the given pokémon to look for is not found!"
)
log_response_trade_proposal_member_proposing = "`[{datetime}]` -- **{member}** created a trade proposal!"
log_response_trade_offer_member_offering = "`[{datetime}]` -- **{member}** offered a pokémon!"
log_response_trade_search_member_searching = "`[{datetime}]` -- **{member}** searched for a pokémon!"
# Embeds
trade_embed_title = "Trading"
trade_embed_description = "Welcome to trading! Please select what you want to do."
trade_proposal_embed_title = "Trading proposal"
trade_proposal_embed_description = (
    "Hello everyone!\n\n I am looking for `{pokemon_search}`!\n I have `{pokemon_offer}` to offer!"
)
trade_proposal_embed_footer = (
    "Trade proposed by: {member}. If you have any interest or would like to negotiate, please contact me!"
)
trade_proposal_embed_field_offering = "Offering:"
trade_proposal_embed_field_search = "Searching:"
trade_offer_embed_title = "Trading offer"
trade_offer_embed_description = "Hello everyone!\n\n I have `{pokemon_offer}` to offer!"
trade_offered_embed_footer = (
    "Trade offered by: {member}. If you have any interest or would like to negotiate, please contact me!"
)
trade_search_embed_title = "Trade search"
trade_search_embed_description = "Hello everyone!\n\n I am looking for `{pokemon_search}`!"
trade_search_embed_footer = (
    "Trade search by: {member}. If you have any interest or would like to negotiate, please contact me!"
)
