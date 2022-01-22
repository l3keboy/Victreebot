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
raid_id_database_error="The generated raid couldn't not be created! A raid with the same ID already exists, please try again! NOTE: PLEASE LET THE SERVER ADMINISTRATOR DELETE THE CREATED EMBED!"
raid_unknown_database_error="The generated raid couldn't be created! Please try again! NOTE: PLEASE LET THE SERVER ADMINISTRATOR DELETE DELETE THE CREATED EMBED!"

raid_successfully_created="The `{raid_type}` is created!"
raid_embed_description="**Raid ID:** {raid_id}\n**Time:** {time}\n**Date:** {date}\n**Location:** [{location}](https://www.google.com/maps/place/{latitude},{longitude})\n**Type:** {raid_type}"
raid_embed_footer="Raid created by: {member} | Total attendees: {attendees}"

raid_unable_to_delete_not_creator_or_enough_permissions="You can't delete this raid because you didn't create it and you don't have the right permissions!"
raid_successfully_deleted="The raid with id: `{id}` successfully deleted!"

raid_unable_to_find="I didn't find the raid with ID: `{id}`!"
raid_unable_to_edit_not_creator_or_enough_permissions="You can't edit this raid because you didn't create it and you don't have the right permissions!"
raid_successfully_edited="The raid with id: `{id}` successfully edited!"

# ------------------------------------------------------------------------- #
# 4_trade #
# ------------------------------------------------------------------------- #
trade_proposal_created=" created a trade proposal!"
trade_proposal_embed_title="Trade proposal"
trade_proposal_embed_description="Hello everyone!\n\n I am looking for `{pokémon_want}`!\n I have `{pokémon_have}` to offer!"
trade_proposal_embed_footer="Trade proposed by: {member}. If you have any interest or would like to negotiate, please contact me!"
trade_proposal_embed_offering="Offering Pokémon:"
trade_proposal_embed_looking_for="Looking for Pokémon:"

trade_offer_created=" created a trade offer!"
trade_offer_embed_title="Trade offer"
trade_offer_embed_description="Hello everyone!\n\n I am offering `{pokémon_have}`!"
trade_offer_embed_footer="Trade offer by: {member}. If you have any interest, please contact me!"
trade_offer_embed_offering="Offering Pokémon:"

trade_search_created=" created a trade search!"
trade_search_embed_title="Trade search"
trade_search_embed_description="Hello everyone!\n\n I am searching for `{pokémon_want}`!"
trade_search_embed_footer="Trade search by: {member}. If you want to trade this Pokémon, please contact me!"
trade_search_embed_looking_for="Looking for Pokémon:"

# ------------------------------------------------------------------------- #
# 5_pokedex #
# ------------------------------------------------------------------------- #
pokedex_sending_dm="Sending the information of `{pokemon}` to your DM!"

# ------------------------------------------------------------------------- #
# 6_pokebattler #
# ------------------------------------------------------------------------- #
pokebattler_sending_dm="Sending the information of `{pokemon}` to your DM!"

# ------------------------------------------------------------------------- #
# 90_stats #
# ------------------------------------------------------------------------- #
server_stats_embed_title="Stats of {guild_name}"
server_stats_embed_description="All stats of the `{guild_name}` server!"
server_stats_embed_raids_created_title="Raids Created:"
server_stats_embed_raids_created_description="✅ | {raids_created}"
server_stats_embed_raids_deleted_title="Raids Deleted:"
server_stats_embed_raids_deleted_description="❌ | {raids_deleted}"
server_stats_embed_raids_completed_title="Raids Completed:"
server_stats_embed_raids_completed_description="🥇 | {raids_completed}"

user_stats_embed_title="Stats of {user_name}"
user_stats_embed_description="All stats of `{user_name}`!"
user_stats_embed_raids_created_title="Raids Created:"
user_stats_embed_raids_created_description="✅ | {raids_created}"
user_stats_embed_raids_participated_title="Raids Participated:"
user_stats_embed_raids_participated_description="🥇 | {raids_participated}"
user_stats_embed_user_locations_title="Active in locations:"
user_stats_embed_user_friend_codes_title="Friend Codes:"
user_stats_embed_no_locations_set="No active locations set!"
user_stats_embed_no_friend_codes_set="No friend codes set!"

# ------------------------------------------------------------------------- #
# 98_profile #
# ------------------------------------------------------------------------- #
profile_added_location="I have added `{location}` to your active locations!"
profile_removed_location="I have removed `{location}` from your active locations!"
profile_no_locations_set="You haven't set any locations!"
profile_specified_location_not_found="I haven't found that location in your active locations!"
profile_added_friend_code="I have added `{friend_code}` to your friend codes!"
profile_removed_friend_code="I have removed `{friend_code}` from your friend codes!"
profile_no_friend_code_set="You haven't set any friend codes!"
profile_specified_friend_code_not_found="I haven't found that friend code in your friend codes!"

# ------------------------------------------------------------------------- #
# 99_explanation #
# ------------------------------------------------------------------------- #
explanation_sending="I am sending the explanation to your DM!"
explanation_embed_footer="This message will be timout in 60 seconds or when someone in the origin server uses a VictreeBot slash comand!"
explanation_author="VictreeBot Explanations"

explanation_location_page_1_title="Explanation about location commands and locations"
explanation_location_page_1_description="Hello! Welcome to the location (commands) help! \nThis manual helps you to get to now the locations and the locations commands! \nUsing the buttons below, you can switch through the different pages!\n\u200b"
explanation_location_page_2_title="/location create [location_type] [name] [latitude] [longitude] | +0 optional"
explanation_location_page_2_description="*Optional: **none***"
explanation_location_page_2_field_1_title="Creating a location"
explanation_location_page_2_field_1_value="A new location can be created using the command `/location create`. This command has 4 required and 0 optional argument.\n\n *Required arguments:*\n - **Location_type:** The location_type gives 2 options: Gym and Pokéstop, choose the location_type you wish to create!\n - **Name:** The name of the location. This argument is not case sensitive (the whole name will be converted to lowercase).\n - **Latitude:** The latidude of the location. This argument is validated.\n - **Longitude:** The longitude og the location. This argument is validated.\n\n *The optional arguments:*\n - **None:** There are no optional arguments!\n\u200b"
explanation_location_page_3_title="/location delete [location_type] [name] | +0 optional"
explanation_location_page_3_description="*Optional: **none***"
explanation_location_page_3_field_1_title="Deleting a location"
explanation_location_page_3_field_1_value="If a location was created by mistake or something isn't right, this location can be deleted using the command `/location delete`. This command has 2 required and 0 optional arguments.\n\n *Required arguments:*\n - **Location_type:** This is the type of the location you wish to delete, two options are given: Gym and Pokéstop.\n - **Name:** The name of the location to delete. This argument is not case sensitive (the whole name will be converted to lowercase).\n\n *Optional arguments:*\n - **None:** There are no optional arguments!\n\u200b"
explanation_location_page_3_field_2_title="Why the combination of location_type and name?"
explanation_location_page_3_field_2_value="This in combination of location_type and name ensures the right location is deleted. When a location is deleted, all corresponding location entries in the database are deleted.\n\u200b"
explanation_location_page_4_title="/location info [location_type] | +1 optional"
explanation_location_page_4_description="*Optional: **Name***"
explanation_location_page_4_field_1_title="Getting info about a location"
explanation_location_page_4_field_1_value="You can get information about one or all locations using the command `/location info`. This command has 1 required and 1 optional argument.\n\n *Required arguments:*\n - **Location_type:** This is the type of the location you wish to get information about, the two options: Gym and Pokéstop are given.\n\n *Optional arguments:*\n - **Name:** The name of the location to get information about, this argument is not case sensitive (the whole name will be converted to lowercase).\n\u200b"
explanation_location_page_4_field_2_title="What happens when I dont set the optional argument?"
explanation_location_page_4_field_2_value="When the name argument is not passed, a list of all locations with the desired location_type is given.\n\u200b"

explanation_raid_page_1_title="Explanation about raid commands and raids"
explanation_raid_page_1_description="Hello! Welcome to the raids (commands) help! \nThis manual helps you to get to now the raids and the raids commands! \nUsing the buttons below, you can switch through the different pages!\n\u200b"
explanation_raid_page_2_title="/raid create [raid_type] [boss] [location] [time] | +1 optional"
explanation_raid_page_2_description="*Optional: **date***"
explanation_raid_page_2_field_1_title="Creating a raid"
explanation_raid_page_2_field_1_value="A new raid can be created using the command `/raid create`. This command has 4 required and 1 optional argument.\n\n *Required arguments:*\n - **Raid_type:** The raid_type gives 3 options: Raid, Mega-raid and EX-raid, choose the raid_type you wish to create!\n - **Boss:** The boss is the desired pokémon, f.e. Pikachu, this argument is not case sensitive and your input will be validated.\n - **Location:** The location is the name of the location where the raid takes place, this argument is also not case sensitive and will be validated.\n - **Time:** The time the raid takes place, f.e. 12:00, this is in military time using the HH:MM format!\n\n *The optional arguments:*\n - **Date:** The date the raid takes place, by default the current date will be used, but you can set a custom date using the DD-MM-YYYY format.\n\u200b"
explanation_raid_page_2_field_2_title="The raid_id"
explanation_raid_page_2_field_2_value="When creating a new raid, a raid_id will be generated. This ID will be linked to the generated raid and can be used to delete or edit the specific raid.\n\u200b"
explanation_raid_page_2_field_3_title="The raid message"
explanation_raid_page_2_field_3_value="Once the raid is being created and all checks (f.e. Pokémon validation) are completed and succesful, the raid message will be send to the configured raids_channel (by default this is: victreebot-raids-channel, but can differ per server!).\n\u200b"
explanation_raid_page_3_title="/raid delete [raid_type] [raid_id] | +0 optional"
explanation_raid_page_3_description="*Optional: **none***"
explanation_raid_page_3_field_1_title="Deleting a raid"
explanation_raid_page_3_field_1_value="If a raid was created by mistake or something isn't right, this raid can be deleted using the command `/raid delete`. This command has 2 required and 0 optional arguments.\n\n *Required arguments:*\n - **Raid_type:** This is the type of the raid you wish to delete, three options are given: Raid, Mega-raid and EX-raid.\n - **Raid_id:** This is the generated id (raid_id) of the raid you wish to delete.\n\n *Optional arguments:*\n - **None:** There are no optional arguments!\n\u200b"
explanation_raid_page_3_field_2_title="Why the combination of raid_type and raid_id?"
explanation_raid_page_3_field_2_value="This in combination of raid_type and raid_id ensures the right raid is deleted. When a raid is deleted the raid message and all corresponding entries in the database are deleted.\n\u200b"
explanation_raid_page_4_title="/raid edit [raid_type] [raid_id] | +5 optional"
explanation_raid_page_4_description="*Optional: **New_type**, **New_boss**, **New_location**, **New_time**, **New_date***"
explanation_raid_page_4_field_1_title="Editing a raid"
explanation_raid_page_4_field_1_value="If raid details are wrong or have changed, you can edit that raid using the command `/raid edit`. This command has 2 required and 5 optional arguments.\n\n *Required arguments:*\n - **Raid_type:** This is the type of the raid you wish to edit, again, the three options: Raid, Mega-raid and EX-raid are given.\n - **Raid_id:** This is the generated id (raid_id) of the raid you wish to edit.\n\n *Optional arguments:*\n - **New_type:** The new type of the raid (the options: Raid, Mega-raid and EX-raid are given)\n - **New_boss:** The new boss.\n - **New_location:** The name of the new location.\n - **New_time:** The new time the raid takes place, in military time using the HH:MM format!.\n - **New_date:** The new date the raid takes place, using the DD-MM-YYYY format.\n\u200b"
explanation_raid_page_4_field_2_title="Why the combination of raid_type and raid_id?"
explanation_raid_page_4_field_2_value="This in combination of raid_type and raid_id ensures the right raid is edited. When a raid is edited the raid message and all corresponding entries in the database will be changed.\n\u200b"
explanation_raid_page_4_field_3_title="What happens if I don't set an optional argument?"
explanation_raid_page_4_field_3_value="If an optional argument is not set (left empty) that value won't change, so you can safely edit one specific detail of the raid."
explanation_raid_page_5_title="Raids"
explanation_raid_page_5_description="Extra useful information regarding raids.\n\u200b"
explanation_raid_page_5_field_1_title="Reacting to a raid"
explanation_raid_page_5_field_1_value="When the raid message is sent, VictreeBot reacts with some emoji's (**Instinct**, **Mystic**, **Valor**, **R**, **1**, **2**, **3**). Using these reactions, you can let the owner, and other users, know if you attend a raid in person (**Instinct**, **Mystic**, **Valor**), if you arrend a raid remotely (**R**) and if you bring others (**1**, **2**, **3**).\n\u200b"
explanation_raid_page_5_field_2_title="My name doesn't appear, what now?"
explanation_raid_page_5_field_2_value="Because of different checks and validations it can take some time (usually not longer than 5 seconds) before your name appears. When multiple users react at once, sometimes issues arrize. When your name doesn't appear or other issues arrize, pleas remove your reaction, wait a minute, and react again!\n\u200b"
explanation_raid_page_5_field_3_title="Raids and statistics"
explanation_raid_page_5_field_3_value="{bot_name} keeps track of statistics regarding raids! When a raid is created, this is added to the user who created it and to the server. When a raid is deleted this is added to the user who deleted it. ONLY when a raid is automatically deleted, this is added to the servers raids completed and to all users who reacted their raids participated! All stats can be requested via the `/stats` commands!\n\u200b"

explanation_profile_page_1_title="Explanation about profile commands and profile"
explanation_profile_page_1_description="Hello! Welcome to the profile (commands) help! \nThis manual helps you to get to now the profile and the profile commands! \nUsing the buttons below, you can switch through the different pages!\n\u200b"
explanation_profile_page_2_title="/profile location_add [location_to_add] | +0 optional"
explanation_profile_page_2_description="*Optional: **none***"
explanation_profile_page_2_field_1_title="Adding a new location to your profile"
explanation_profile_page_2_field_1_value="A new location can be added to your profile using the command `/profile location_add`. This command has 1 required and 0 optional argument.\n\n *Required arguments:*\n - **Location_to_add:** The location_to_add is the name of the location to add. This argument is not case sensitive (the whole name will be capitalized).\n\n *Optional arguments:*\n - **None:** There are no optional arguments!\n\u200b"
explanation_profile_page_3_title="/profile location_remove [location_to_remove] | +0 optional"
explanation_profile_page_3_description="*Optional: **none***"
explanation_profile_page_3_field_1_title="Removing a location from your profile"
explanation_profile_page_3_field_1_value="If you want to remove a location from your profile, you can do this by using the command `/profile location_remove`. This command has 1 required and 0 optional arguments.\n\n *Required arguments:*\n - **Location_to_remove:** The location_to_remove is the name of the location to remove. This argument is not case sensitive (the whole name will be capitalized).\n\n *Optional arguments:*\n - **None:** There are no optional arguments!\n\u200b"
explanation_profile_page_4_title="/profile friendcode_add [friendcode_to_add] | +0 optional"
explanation_profile_page_4_description="*Optional: **none***"
explanation_profile_page_4_field_1_title="Adding a friend code to your profile"
explanation_profile_page_4_field_1_value="If you want to add a friend code so that others can become friend with you, you can do this using the `/profile friendcode_add`. This command has 1 required and 0 optional argument.\n\n *Required arguments:*\n - **Friendcode_to_add:** This is the friendcode you want to add. This must be in format XXXX-XXXX-XXXX.\n\n *Optional arguments:*\n - **None:** There are no optional arguments!\n\u200b"
explanation_profile_page_5_title="/profile friendcode_remove [friendcode_to_remove] | +0 optional"
explanation_profile_page_5_description="*Optional: **none***"
explanation_profile_page_5_field_1_title="Removing a friend code to your profile"
explanation_profile_page_5_field_1_value="If you want to remove a friend code, f.e. because you are not using that account anymore, you can do this using the `/profile friendcode_remove`. This command has 1 required and 0 optional argument.\n\n *Required arguments:*\n - **Friendcode_to_remove:** This is the friendcode you want to remove. This must be in format XXXX-XXXX-XXXX.\n\n *Optional arguments:*\n - **None:** There are no optional arguments!\n\u200b"

explanation_stats_page_1_title="Explanation about stats commands and stats"
explanation_stats_page_1_description="Hello! Welcome to the stats (commands) help! \nThis manual helps you to get to now the stats and the stats commands! \nUsing the buttons below, you can switch through the different pages!\n\u200b"
explanation_stats_page_2_title="/stats server | +0 optional"
explanation_stats_page_2_description="*Optional: **none***"
explanation_stats_page_2_field_1_title="Getting the stats of the server"
explanation_stats_page_2_field_1_value="You can view the stats of the server using the command `/stats server`. This command has 0 required and 0 optional argument.\n\n *Required arguments:*\n - **None:** There are no required arguments!\n\n *Optional arguments:*\n - **None:** There are no optional arguments!\n\u200b"
explanation_stats_page_3_title="/stats user [user] | +0 optional"
explanation_stats_page_3_description="*Optional: **none***"
explanation_stats_page_3_field_1_title="Getting stats of the user"
explanation_stats_page_3_field_1_value="You can view the stats of a user using the command `/stats user`. This command has 1 required and 0 optional arguments.\n\n *Required arguments:*\n - **User:** The user you want to get the stats about.\n\n *Optional arguments:*\n - **None:** There are no optional arguments!\n\u200b"
explanation_stats_page_4_title="Stats"
explanation_stats_page_4_description="Extra useful information regarding stats"
explanation_stats_page_4_field_1_title="Which stats are collected for a server?"
explanation_stats_page_4_field_1_value="There are currently three different stats collected for a server, these are: `raids_created`, `raids_deleted` and `raids_completed`! Just like the names suggests, the raids_created is updated when a raid is created and raids_deleted gets updated when a raid is deleted. Raids completed is only updated when a raid is automatically deleted by {bot_name}!\n\u200b"
explanation_stats_page_4_field_2_title="Which stats are collected for a user?"
explanation_stats_page_4_field_2_value="There are currently two different stats collected for a user, these are: `raids_created` and `raids_participated`! Just like the name suggests, the raids_created is updated when a raid is created. Raids_participated is only updated when a raid is automatically deleted by {bot_name}!\n\u200b"

explanation_trade_page_1_title="Explanation about trade commands and trade"
explanation_trade_page_1_description="Hello! Welcome to the trade (commands) help! \nThis manual helps you to get to now the stats and the stats commands! \nUsing the buttons below, you can switch through the different pages!\n\u200b"
explanation_trade_page_2_title="/trade proposal [pokémon_have] [pokémon_want] | +0 optional"
explanation_trade_page_2_description="*Optional: **none***"
explanation_trade_page_2_field_1_title="Proposing a trade"
explanation_trade_page_2_field_1_value="You can propose a raid to other users by using the command `/trade proposal`. This command has 2 required and 0 optional argument.\n\n *Required arguments:*\n - **Pokémon_have:** This is the pokemon you have and you want to trade with.\n - **Pokémon_want:** This is the Pokémon you want in trade of the Pokémon you have.\n\n *Optional arguments:*\n - **None:** There are no optional arguments!\n\u200b"
explanation_trade_page_3_title="/trade offer [pokémon_have] | +0 optional"
explanation_trade_page_3_description="*Optional: **none***"
explanation_trade_page_3_field_1_title="Offering a Pokémon for a trade"
explanation_trade_page_3_field_1_value="If you have a Pokémon you want to trade but don't specificaly know what Pokémon you want in return, you can offer this Pokémon using the command `/trade offer`. This command has 1 required and 0 optional arguments.\n\n *Required arguments:*\n - **Pokémon_have:** This is the pokemon you have and you want to trade with.\n\n *Optional arguments:*\n - **None:** There are no optional arguments!\n\u200b"
explanation_trade_page_4_title="/trade search [pokémon_want] | +0 optional"
explanation_trade_page_4_description="*Optional: **none***"
explanation_trade_page_4_field_1_title="Looking for a Pokémon trade"
explanation_trade_page_4_field_1_value="If you are looking a Pokémon but don't specificaly know what Pokémon you have in return, you can search this Pokémon using the command `/trade search`. This command has 1 required and 0 optional arguments.\n\n *Required arguments:*\n - **Pokémon_want:** This is the pokemon you want.\n\n *Optional arguments:*\n - **None:** There are no optional arguments!\n\u200b"

# ------------------------------------------------------------------------- #
# ERRORS #
# ------------------------------------------------------------------------- #
# General
error_command_in_development="The command: `{command}` is in development and will be added later. Your input: {input}!"
error_request_failed="I am sorry, the request failed with status code: `{status_code}`!"
# Validate
error_float_latitude_invalid="I am sorry, the given `latitude` can't be converted to float!"
error_float_longitude_invalid="I am sorry, the given `longitude` can't be converted to float!"
error_latitude_invalid="I am sorry, the given `latitude` is invalid! Your input: `{latitude}`!"
error_longitude_invalid="I am sorry, the given `longitude` is invalid! Your input: `{longitude}`!"
error_friend_code_invalid="I am sorry, the given `friend code` is invalid! Your input: `{friend_code}`!"
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

# 4_trade
log_channel_trade_proposal_created="`[{datetime}]` - **{member}** created a trade proposal!"
log_channel_trade_offer_created="`[{datetime}]` - **{member}** created a trade offer!"
log_channel_trade_search_created="`[{datetime}]` - **{member}** created a trade search!"

# 5_pokedex
log_channel_pokedex_request_failed="`[{datetime}]` - **{member}** tried to access the Pokédex but the request failed with status code: `{status_code}`!"
log_channel_pokedex_requested="`[{datetime}]` - **{member}** requested the details of a Pokémon (Pokédex command)!"

# 6_pokebattler
log_channel_pokebattler_request_failed="`[{datetime}]` - **{member}** tried to access the Pokébattler but the request failed with status code: `{status_code}`!"
log_channel_pokebattler_requested="`[{datetime}]` - **{member}** requested the details of a Pokémon (Pokébattler command)!"

# 90_stats
log_channel_server_stats_requested="`[{datetime}]` - **{member}** requested the stats of the server!"
log_channel_user_stats_requested="`[{datetime}]` - **{member}** requested the stats of `{user_name}`!"

# 98_profile
log_channel_profile_location_added="`[{datetime}]` - **{member}** added a location to their profile!"
log_channel_profile_location_removed="`[{datetime}]` - **{member}** removed a location from their profile!"
log_channel_profile_friendcode_added="`[{datetime}]` - **{member}** added a friend code to their profile!"
log_channel_profile_friendcode_removed="`[{datetime}]` - **{member}** removed a friend code from their profile!"

# 99_explanation
log_channel_explanation_location_sending="`[{datetime}]` - **{member}** requested the explanation for `location commands`, I am sending it to their DM!"
log_channel_explanation_location_sending_failed="`[{datetime}]` - **{member}** requested the explanation for `locations commands`, I tried to send it to their DM, but the execution failed!"
log_channel_explanation_raid_sending="`[{datetime}]` - **{member}** requested the explanation for `raid commands`, I am sending it to their DM!"
log_channel_explanation_raid_sending_failed="`[{datetime}]` - **{member}** requested the explanation for `raid commands`, I tried to send it to their DM, but the execution failed!"
log_channel_explanation_profile_sending="`[{datetime}]` - **{member}** requested the explanation for `profile commands`, I am sending it to their DM!"
log_channel_explanation_profile_sending_failed="`[{datetime}]` - **{member}** requested the explanation for `profile commands`, I tried to send it to their DM, but the execution failed!"
log_channel_explanation_stats_sending="`[{datetime}]` - **{member}** requested the explanation for `stats commands`, I am sending it to their DM!"
log_channel_explanation_stats_sending_failed="`[{datetime}]` - **{member}** requested the explanation for `stats commands`, I tried to send it to their DM, but the execution failed!"
log_channel_explanation_trade_sending="`[{datetime}]` - **{member}** requested the explanation for `trade commands`, I am sending it to their DM!"
log_channel_explanation_trade_sending_failed="`[{datetime}]` - **{member}** requested the explanation for `trade commands`, I tried to send it to their DM, but the execution failed!"