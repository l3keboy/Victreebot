from types import ModuleType

import hikari
import hikari.interactions.base_interactions
import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.languages import en


class LocationLongLatModal(lightbulb.components.Modal):
    _language: str
    _language_helper: ModuleType
    selected_btn: str | None = None
    given_location_long: str | None = None
    given_location_lat: str | None = None

    def __init__(self, language: str, location_type: str) -> None:
        self._language = language
        supported_language_helper = SUPPORTED_LANGUAGES.get(self._language)
        self._language_helper = en if supported_language_helper is None else supported_language_helper

        self.add_text_field_title_input_long = self.add_short_text_input(
            self._language_helper.location_longitude_modal_text_input_title.format(location=location_type.strip("'")),
            custom_id="location_longitude",
            placeholder=self._language_helper.location_longitude_modal_text_input_placeholder,
            required=True
        )

        self.add_text_field_title_input_lat = self.add_short_text_input(
            self._language_helper.location_latitude_modal_text_input_title.format(location=location_type.strip("'")),
            custom_id="location_latitude",
            placeholder=self._language_helper.location_latitude_modal_text_input_placeholder,
            required=True
        )

    async def on_submit(self, ctx: lightbulb.components.ModalContext) -> None:
        await ctx.interaction.create_initial_response(
            hikari.interactions.base_interactions.ResponseType.DEFERRED_MESSAGE_UPDATE
        )
        self.selected_btn = ctx.interaction.custom_id
        self.given_location_long = ctx.value_for(self.add_text_field_title_input_long)
        self.given_location_lat = ctx.value_for(self.add_text_field_title_input_lat)