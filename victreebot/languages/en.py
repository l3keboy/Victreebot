# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# GLOBAL VARIABLES #
# ------------------------------------------------------------------------- #
# Footer
embed_footer="Info requested by: {member}! This embed will show for {auto_delete} seconds!"
# Logging translations
log_errors="Errors"
log_info="Info requests"
log_settings_changed="Setting changes"
# Other
enabled="Enabled"
disabled="Disabled"
not_in_use="Not in use!"
no_reason_specified="*No reason specified!*"
# Dicts
STATUS_CODES={
    "200": "API Request OK!",
    "400": "Bad Request",
    "401": "Unauthorized",
    "403": "API Request Forbidden",
    "404": "API Request Not Found",
    "429": "Too many requests",
    "503": "API Unavailable",
}
CHANNEL_TYPES={
    "DM": "DM channel",
    "GROUP_DM": "Group DM channel",
    "GUILD_CATEGORY": "Category channel",
    "GUILD_NEWS": "News channel",
    "GUILD_STAGE": "Stage channel",
    "GUILD_STORE": "Store channel",
    "GUILD_TEXT": "Text channel",
    "GUILD_VOICE": "Voice channel",
}

# ------------------------------------------------------------------------- #
# GLOBAL ERRORS #
# ------------------------------------------------------------------------- #
error_response_not_enough_permissions_for_channel="Oops! It looks like I don't have enough permissions to use that channel!"
error_response_not_a_text_channel="Oops! It looks like that the given channel is not a text channel!"
error_response_not_a_voice_channel="Oops! It looks like that the given channel is not a voice channel!"
error_response_not_a_valid_id="Oops! It looks like that the given value is not an valid ID!"
error_response_not_a_valid_emoji="Oops! It looks like that the given emoji is not a valid emoji!"





# ------------------------------------------------------------------------- #
# settings.py #
# ------------------------------------------------------------------------- #
# Responses
response_update_raids_channel_success_changed="I have changed the raids channel to `{raids_channel} - {raids_channel_id}`!"
response_update_raids_channel_failed_changed="Oops! Something went wrong while trying to change the raids channel to `{raids_channel} - {raids_channel_id}`!"
response_settings_update_general_failed="Oops! Something went wrong while trying to update the general setting(s)!"
response_settings_update_general_success="I have changed the general setting(s)!"
response_settings_update_moderation_failed="Oops! Something went wrong while trying to update the moderation setting(s)!"
response_settings_update_moderation_success="I have changed the moderation setting(s)!"
# Log responses
log_response_update_raids_channel_failed_not_enough_privileges="`[{datetime}]` -- **{member}** tried changing the raids channel to a channel where I don't have enough permissions for!"
log_response_update_raids_channel_failed_not_a_text_channel="`[{datetime}]` -- **{member}** tried changing the raids channel but didn't gave a valid text channel!"
log_response_update_raids_channel_success_changed="`[{datetime}]` -- **{member}** changed the raids channel to `{raids_channel} - {raids_channel_id}`!"
log_response_update_raids_channel_failed_changed="`[{datetime}]` -- **{member}** tried changing the raids channel to `{raids_channel} - {raids_channel_id}` but failed!"
log_response_settings_update_general_failed="`[{datetime}]` -- **{member}** tried updating general setting(s)! But something went wrong!"
log_response_settings_update_general_success="`[{datetime}]` -- **{member}** updated general setting(s)!"
log_response_settings_update_moderation_failed="`[{datetime}]` -- **{member}** tried updating moderation setting(s)! But something went wrong!"
log_response_settings_update_moderation_success="`[{datetime}]` -- **{member}** updated moderation setting(s)!"
# Embeds





# ------------------------------------------------------------------------- #
# log_settings.py #
# ------------------------------------------------------------------------- #
# Responses
response_update_logs_channel_success_unset="I have removed the logs channel! Note: Due to this change, I will not send log messages regarding interactions/events for this server!"
response_update_logs_channel_success_changed="I have changed the logs channel to `{logs_channel} - {logs_channel_id}`!"
response_update_logs_channel_failed_unset="Oops! Something went wrong while trying to remove the logs channel!"
response_update_logs_channel_failed_changed="Oops! Something went wrong while trying to set the logs channel to `{logs_channel} - {logs_channel_id}`!"
response_log_settings_update_general_events_failed="Oops! Something went wrong while trying to change the general events log setting(s)!"
response_log_settings_update_general_events_success="I have changed the general events log setting(s)!"
# Log responses
log_response_update_logs_channel_failed_not_enough_privileges="`[{datetime}]` -- **{member}** tried changing the logs channel to a channel where I don't have enough permissions for!"
log_response_update_logs_channel_failed_not_a_text_channel="`[{datetime}]` -- **{member}** tried changing the logs channel but didn't gave a valid text channel!"
log_response_update_logs_channel_success_unset="`[{datetime}]` -- **{member}** removed the logs channel from this server! Note: Due to this change, I will not send log messages regarding interactions/events for this server!"
log_response_update_logs_channel_success_changed="`[{datetime}]` -- **{member}** changed the logs channel to `{logs_channel} - {logs_channel_id}`!"
log_response_update_logs_channel_failed_unset="`[{datetime}]` -- **{member}** tried removing the logs channel but failed!"
log_response_update_logs_channel_failed_changed="`[{datetime}]` -- **{member}** tried changing the logs channel to `{logs_channel} - {logs_channel_id}` but failed!"
log_response_log_settings_update_general_events_failed="`[{datetime}]` -- **{member}** tried updating general events log setting(s)! But something went wrong!"
log_response_log_settings_update_general_events_success="`[{datetime}]` -- **{member}** updated general events log setting(s)!"
# Embeds