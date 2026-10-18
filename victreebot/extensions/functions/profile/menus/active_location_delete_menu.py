# Copyright (c) 2022-present l3keboy

from types import ModuleType

import hikari
import hikari.interactions.base_interactions
import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.languages import en


class ActiveLocationDeleteModal(lightbulb.components.Modal):
    _language: str
    _language_helper: ModuleType
    selected_btn: str | None = None
    given_active_location: str | None = None

    def __init__(self, language: str) -> None:
        self._language = language
        supported_language_helper = SUPPORTED_LANGUAGES.get(self._language)
        self._language_helper = en if supported_language_helper is None else supported_language_helper

        self.add_text_field_title_input = self.add_short_text_input(
            self._language_helper.profile_modal_delete_active_locations_text_input_title,
            custom_id="active_locations",
            placeholder=self._language_helper.profile_modal_delete_active_locations_text_input_placeholder,
        )

    async def on_submit(self, ctx: lightbulb.components.ModalContext) -> None:
        await ctx.interaction.create_initial_response(
            hikari.interactions.base_interactions.ResponseType.DEFERRED_MESSAGE_UPDATE
        )
        self.selected_btn = ctx.interaction.custom_id
        self.given_active_location = ctx.value_for(self.add_text_field_title_input)
