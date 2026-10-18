# Copyright (c) 2022-present l3keboy

from collections.abc import Sequence

import hikari
import hikari.errors


# ------------------------------------------------------------------------- #
# DiscordService CLASS #
# ------------------------------------------------------------------------- #
class DiscordService:
    """Provide a service to interact with the Discord API using hikari."""

    bot: hikari.RESTApp

    def __init__(self, token: str) -> None:
        """Initialize the DiscordService."""
        self.token = token
        self.bot = hikari.RESTApp()

    # Lifetime
    async def start(self) -> None:
        """Start the DiscordService."""
        await self.bot.start()

    async def close(self) -> None:
        """Close the DiscordService."""
        await self.bot.close()

    # Methods
    async def delete_message(self, channel_id: hikari.Snowflake | int, message_id: hikari.Snowflake | int) -> None:
        """Try to delete a message from a channel in Discord."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.delete_message(channel_id, message_id)
        except hikari.errors.HikariError:
            return None

    async def delete_emoji(
        self,
        guild_id: hikari.Snowflake | int,
        emoji_id: hikari.Snowflake | int,
        reason: str | hikari.UndefinedType = hikari.UNDEFINED,
    ) -> None:
        """Try to delete an emoji from a guild in Discord."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.delete_emoji(guild_id, emoji_id, reason=reason)
        except hikari.errors.HikariError:
            return None

    async def delete_role(
        self,
        guild_id: hikari.Snowflake | int,
        role_id: hikari.Snowflake | int,
        reason: str | hikari.UndefinedType = hikari.UNDEFINED,
    ) -> None:
        """Try to delete an role from a guild in Discord."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.delete_role(guild_id, role_id, reason=reason)
        except hikari.errors.HikariError:
            return None

    async def delete_channel(
        self, channel_id: hikari.Snowflake | int, reason: str | hikari.UndefinedType = hikari.UNDEFINED
    ) -> hikari.PartialChannel | None:
        """Try to delete an channel from a guild in Discord."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.delete_channel(channel_id, reason=reason)
        except hikari.errors.HikariError:
            return None

    async def get_guild_members(self, guild_id: hikari.Snowflake | int) -> Sequence[hikari.Member] | None:
        """Try to fetch all guild members from Discord."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.fetch_members(guild_id)
        except hikari.errors.HikariError:
            return None

    async def get_guild_emojis(self, guild_id: hikari.Snowflake | int) -> Sequence[hikari.KnownCustomEmoji]:
        """Try to fetch all guild members from Discord."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.fetch_guild_emojis(guild_id)
        except hikari.errors.HikariError:
            return []

    async def get_guild_roles(self, guild_id: hikari.Snowflake | int) -> Sequence[hikari.Role]:
        """Try to fetch all guild roles from Discord."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.fetch_roles(guild_id)
        except hikari.errors.HikariError:
            return []

    async def get_guild_channels(self, guild_id: hikari.Snowflake | int) -> Sequence[hikari.PartialChannel]:
        """Try to fetch all guild roles from Discord."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.fetch_guild_channels(guild_id)
        except hikari.errors.HikariError:
            return []

    async def get_my_user(self) -> hikari.OwnUser | None:
        """Try to fetch all guild roles from Discord."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.fetch_my_user()
        except hikari.errors.HikariError:
            return None

    async def get_emoji(
        self, guild_id: hikari.Snowflake | int, emoji_id: hikari.Snowflake | int
    ) -> hikari.KnownCustomEmoji | None:
        """Try to fetch all guild roles from Discord."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.fetch_emoji(guild_id, emoji_id)
        except hikari.errors.HikariError:
            return None

    async def get_message(
        self, channel_id: hikari.Snowflake | int, message_id: hikari.Snowflake | int
    ) -> hikari.Message | None:
        """Try to fetch all guild roles from Discord."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.fetch_message(channel_id, message_id)
        except hikari.errors.HikariError:
            return None

    async def get_member(
        self, guild_id: hikari.Snowflake | int, member_id: hikari.Snowflake | int
    ) -> hikari.Member | None:
        """Try to fetch all guild roles from Discord."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.fetch_member(guild_id, member_id)
        except hikari.errors.HikariError:
            return None

    async def get_guild_channel(self, channel_id: hikari.Snowflake | int) -> hikari.PartialChannel | None:
        """Try to fetch a guilds channel from Discord."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.fetch_channel(channel_id)
        except hikari.errors.HikariError:
            return None

    async def get_guild_role(
        self, guild_id: hikari.Snowflake | int, role_id: hikari.Snowflake | int
    ) -> hikari.Role | None:
        """Try to fetch a guilds channel from Discord."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.fetch_role(guild_id, role_id)
        except hikari.errors.HikariError:
            return None

    async def create_message(
        self,
        channel_id: hikari.Snowflake | int,
        content: str | None,
        embeds: Sequence[hikari.Embed] = [],
        components: Sequence[hikari.api.ComponentBuilder] = [],
    ) -> hikari.Snowflake | None:
        """Send a message to a channel."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return (await client.create_message(channel_id, content, embeds=embeds, components=components)).id
        except hikari.errors.HikariError:
            return None

    async def create_emoji(
        self,
        guild_id: hikari.Snowflake | int,
        name: str,
        image: hikari.Resourceish,
        reason: str | hikari.UndefinedType = hikari.UNDEFINED,
    ) -> hikari.Snowflake | None:
        """Create an emoji in a guild."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return (await client.create_emoji(guild_id, name, image, reason=reason)).id
        except hikari.errors.HikariError:
            return None

    async def create_role(
        self,
        guild_id: hikari.Snowflake | int,
        name: str,
        colour: hikari.Color,
        reason: str | hikari.UndefinedType = hikari.UNDEFINED,
    ) -> hikari.Role | None:
        """Create an emoji in a guild."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.create_role(guild_id, name=name, colour=colour, reason=reason)
        except hikari.errors.HikariError:
            return None

    async def create_guild_text_channel(
        self,
        guild_id: hikari.Snowflake | int,
        name: str,
        permission_overwrites: Sequence[hikari.PermissionOverwrite] | hikari.UndefinedType = hikari.UNDEFINED,
        reason: str | hikari.UndefinedType = hikari.UNDEFINED,
    ) -> hikari.GuildTextChannel | None:
        """Create an emoji in a guild."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                return await client.create_guild_text_channel(
                    guild_id, name=name, permission_overwrites=permission_overwrites, reason=reason
                )
        except hikari.errors.HikariError:
            return None

    async def add_reaction(
        self,
        channel_id: hikari.Snowflake | int,
        message_id: hikari.Snowflake | int,
        emoji: str,
        emoji_id: hikari.UndefinedOr[hikari.SnowflakeishOr[hikari.CustomEmoji]] = hikari.UNDEFINED,
    ) -> None:
        """Create an emoji in a guild."""
        try:
            async with self.bot.acquire(self.token, "bot") as client:
                await client.add_reaction(channel_id, message_id, emoji, emoji_id)
        except hikari.errors.HikariError:
            return
