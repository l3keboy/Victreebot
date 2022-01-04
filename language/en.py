# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks and Martijn Verlind                              #
# ------------------------------------------------------------------------- #

embed_footer="Info requested by: {member}. This dialog will show for {auto_delete_time} seconds."

# ------------------------------------------------------------------------- #
# SETTINGS UPDATED #
# ------------------------------------------------------------------------- #
updated_language="The language of this server is now set to `{language}`!"
updated_gmt="The timezone of this server is now set to `{gmt}`!"
updated_auto_delete_time="The auto delete time for this server is now set to `{seconds} seconds`!"
updated_raids_channel_changed="The raids channel for this server is now set to `{channel}`!"
updated_raids_channel_removed="The raids channel for this server is now `removed`!"
updated_logs_channel_changed="The logs channel for this server is now set to `{channel}`!"
updated_logs_channel_removed="The logs channel for this server is now `removed`!"

# ------------------------------------------------------------------------- #
# 2_location #
# ------------------------------------------------------------------------- #
create_success="I have successfully created the {location_type}!"
create_failed="Something went wrong while creating the {location_type}!"
delete_success="I have successfully deleted the {location_type}!"
delete_failed="Something went wrong while deleting the {location_type}!"
info_embed_location_does_not_exists="The `{location_type}` with the name `{location}` does not exist!"
info_embed_title="Location information"
info_embed_discription="Location: `{location}` -- Type: `{location_type}`."
info_google_maps="View location on Google Maps!"
info_embed_location_info_field_title="Location information:"
info_embed_location_info_field_value="Latitude: `{latitude}`\n Longitude: `{longitude}`"
info_embed_location_google_maps_field_title="Google Maps:"
info_embed_location_google_maps_field_value="[Go to google maps!]({link})"
info_paginate_embed_title="Locations list"
info_paginate_embed_description="List of all locations for this guild!"
info_paginate_embed_locations_title="Locations:"
info_paginate_embed_no_results="There are no `{location_type}'s` available in this server!"

# ------------------------------------------------------------------------- #
# ERRORS #
# ------------------------------------------------------------------------- #
# General
error_command_in_development="The command: `{command}` is in development and will be added later. Your input: {input}!"
error_timed_out="Timed Out!"
# 2_location
error_latitude_invalid="I am sorry, the given `latitude` is invalid! Your input: `{latitude}`!"
error_longitude_invalid="I am sorry, the given `longitude` is invalid! Your input: `{longitude}`!"