import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, Option, SlashCommandGroup
from discord import InteractionContextType as ict

import time as tm
import asyncio

import os

import emoji as em

import log_helper

import translation

import config

import database

logger = log_helper.Logger("Settings")


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    languages = translation.get_languages()


    ######################################################
    # Standard Roles
    ######################################################
    stardardRolesGroup = SlashCommandGroup(name="standard_roles", description="Manage the bot's settings", contexts=[ict.guild], default_member_permissions=discord.Permissions(administrator=True))

    @stardardRolesGroup.command(name="add", description="Add a standard role to the guild")
    async def add(self, ctx, role: discord.Role):
        # Check if the role is already a standard role
        if database.execute_read_query(f"SELECT * FROM standard_roles WHERE guild_id={ctx.guild.id} AND role_id={role.id}"):
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "standard_role_already_added_title"), description=translation.get_translation(ctx.user.id, "standard_role_already_added", role=role.mention), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        # Check if the role limit has been reached
        if len(database.execute_read_query(f"SELECT * FROM standard_roles WHERE guild_id={ctx.guild.id}")) >= config.load_value("standard_roles_limit"):
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "standard_roles_limit_reached_title"), description=translation.get_translation(ctx.user.id, "standard_roles_limit_reached", limit=config.load_value("standard_roles_limit")), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        # Add a standard role to the guild
        logger.log(f"Adding standard role {role.name}({role.id}) to {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        database.execute_query(f"INSERT INTO standard_roles (guild_id, role_id) VALUES ({ctx.guild.id}, {role.id})")
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "standard_role_added_title"), description=translation.get_translation(ctx.user.id, "standard_role_added", role=role.mention), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)

    @stardardRolesGroup.command(name="remove", description="Remove a standard role from the guild")
    async def remove(self, ctx, role: discord.Role):
        # Check if the role is not a standard role
        if not database.execute_read_query(f"SELECT * FROM standard_roles WHERE guild_id={ctx.guild.id} AND role_id={role.id}"):
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "standard_role_not_added_title"), description=translation.get_translation(ctx.user.id, "standard_role_not_added", role=role.mention), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        # Remove a standard role from the guild
        logger.log(f"Removing standard role {role.name}({role.id}) from {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        database.execute_query(f"DELETE FROM standard_roles WHERE guild_id={ctx.guild.id} AND role_id={role.id}")
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "standard_role_removed_title"), description=translation.get_translation(ctx.user.id, "standard_role_removed", role=role.mention), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)

    @stardardRolesGroup.command(name="list", description="List all standard roles in the guild")
    async def list(self, ctx):
        # List all standard roles in the guild
        logger.log(f"Listing standard roles in {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        roles = database.execute_read_query(f"SELECT role_id FROM standard_roles WHERE guild_id={ctx.guild.id}")
        if not roles:
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "standard_roles_list_title"), description=translation.get_translation(ctx.user.id, "no_standard_roles"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        role_mentions = []
        for role in roles:
            role_mentions.append(ctx.guild.get_role(role[0]).mention)
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "standard_roles_list_title"), description=translation.get_translation(ctx.user.id, "standard_roles_list", roles=", \n".join(role_mentions)), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)


    @slash_command(name="language", description="Change the bot's language")
    async def language(self, ctx, language: Option(str, "The language you want to use", choices=languages)): # type: ignore
        # Change the bot's language
        logger.log(f"Changing language to {language} for {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        database.execute_query(f"UPDATE users SET language_code='{language}' WHERE id={ctx.user.id}")
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "language_changed_title"), description=translation.get_translation(ctx.user.id, "language_changed", language=language), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)


    ######################################################
    # Custom Channels
    ######################################################
    customChannelsGroup = SlashCommandGroup(name="custom_channels", description="Manage the bot's settings", contexts=[ict.guild], default_member_permissions=discord.Permissions(administrator=True))

    @customChannelsGroup.command(name="setup", description="Setup the bot's custom channels")
    async def setup(self, ctx):
        # Create a category for the custom channels
        logger.log(f"Setting up custom channels in {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        category = await ctx.guild.create_category("Custom Channels")

        # Create a channel where the bot will create channels
        create_channel = await ctx.guild.create_voice_channel("Create Channel", category=category)
        database.execute_query(f"INSERT INTO settings (guild_id, setting_name, setting_value) VALUES ({ctx.guild.id}, 'create_channel', {create_channel.id})")
        logger.log(f"Setting create channel to {create_channel.name}({create_channel.id}) in {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)

        # Create a channel where the bot will send requests
        request_channel = await ctx.guild.create_text_channel("Request Channel", category=category)
        database.execute_query(f"INSERT INTO settings (guild_id, setting_name, setting_value) VALUES ({ctx.guild.id}, 'request_channel', {request_channel.id})")
        logger.log(f"Setting request channel to {request_channel.name}({request_channel.id}) in {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)

        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "custom_channels_setup_title"), description=translation.get_translation(ctx.user.id, "custom_channels_setup", create_channel=create_channel.mention, request_channel=request_channel.mention), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)
        logger.log(f"Custom channels setup in {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.SUCCESS)

    @customChannelsGroup.command(name="delete", description="Delete the bot's custom channels")
    async def delete(self, ctx):
        # Delete the category for the custom channels
        logger.log(f"Deleting custom channels in {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        create_channel = int(database.execute_read_query(f"SELECT * FROM settings WHERE guild_id = {ctx.guild.id} AND setting_name = 'create_channel'")[0][2])
        create_channel = ctx.guild.get_channel(create_channel)
        request_channel = int(database.execute_read_query(f"SELECT * FROM settings WHERE guild_id = {ctx.guild.id} AND setting_name = 'request_channel'")[0][2])
        request_channel = ctx.guild.get_channel(request_channel)
        category = create_channel.category
        for channel in category.channels:
            await channel.delete()
        await category.delete()
        logger.log(f"Custom channels deleted in {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.SUCCESS)
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "custom_channels_deleted_title"), description=translation.get_translation(ctx.user.id, "custom_channels_deleted"), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)


    @customChannelsGroup.command(name="force_delete", description="Delete a custom channel from the guild")
    async def delete(self, ctx, channel: discord.VoiceChannel):
        # Delete a custom channel from the guild
        logger.log(f"Deleting custom channel {channel.name}({channel.id}) from {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        data = database.execute_read_query(f"SELECT * FROM custom_channels WHERE channel_id = {channel.id}")
        if not data:
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "custom_channel_title"), description=translation.get_translation(ctx.user.id, "custom_channel_not_found"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        
        channel = ctx.guild.get_channel(int(data[0][1]))
        await channel.delete()
        database.execute_query(f"DELETE FROM custom_channels WHERE channel_id = {channel.id}")

        joinChannel = database.execute_read_query(f"SELECT * FROM join_channels WHERE owner_id = {data[0][0]} AND guild_id = {ctx.guild.id}")
        if joinChannel:
            joinChannel = ctx.guild.get_channel(int(joinChannel[0][1]))
            await joinChannel.delete()
            database.execute_query(f"DELETE FROM join_channels WHERE owner_id = {data[0][0]} AND guild_id = {ctx.guild.id}")

        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "custom_channel_title"), description=translation.get_translation(ctx.user.id, "custom_channel_deleted", channel=channel.mention), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)


    ######################################################
    # Auto Threads
    ######################################################

    autoThreadsGroup = SlashCommandGroup(name="auto_threads", description="Manage the bot's settings", contexts=[ict.guild], default_member_permissions=discord.Permissions(administrator=True))

    @autoThreadsGroup.command(name="add", description="Add an auto thread to the guild")
    async def add(self, ctx, channel: discord.TextChannel, title: str):
        # Check if the channel is already an auto thread
        if database.execute_read_query(f"SELECT * FROM auto_threads WHERE guild_id={ctx.guild.id} AND channel_id={channel.id}"):
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_thread"), description=translation.get_translation(ctx.user.id, "auto_thread_already_added", channel=channel.mention), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        # Check if the auto thread limit has been reached
        if len(database.execute_read_query(f"SELECT * FROM auto_threads WHERE guild_id={ctx.guild.id}")) >= config.load_value("auto_threads_limit"):
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_threads"), description=translation.get_translation(ctx.user.id, "auto_threads_limit_reached", limit=config.load_value("auto_threads_limit")), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        # Check if the Channel is a Text Channel
        if not channel.type == discord.ChannelType.text:
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_thread"), description=translation.get_translation(ctx.user.id, "auto_thread_not_text_channel", channel=channel.mention), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        # Add an auto thread to the guild
        logger.log(f"Adding auto thread {channel.name}({channel.id}) to {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        # Use parameterized queries to prevent SQL injection and handle special characters
        database.execute_query(
            "INSERT INTO auto_threads (guild_id, channel_id, thread_title) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE thread_title=%s",
            (ctx.guild.id, channel.id, title, title)
        )
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_thread"), description=translation.get_translation(ctx.user.id, "auto_thread_added", channel=channel.mention, title=title), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)

    @autoThreadsGroup.command(name="remove", description="Remove an auto thread from the guild")
    async def remove(self, ctx, channel: discord.TextChannel):
        # Check if the channel is not an auto thread
        if not database.execute_read_query(f"SELECT * FROM auto_threads WHERE guild_id={ctx.guild.id} AND channel_id={channel.id}"):
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_thread"), description=translation.get_translation(ctx.user.id, "auto_thread_not_added", channel=channel.mention), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        # Remove an auto thread from the guild
        logger.log(f"Removing auto thread {channel.name}({channel.id}) from {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        database.execute_query(f"DELETE FROM auto_threads WHERE guild_id={ctx.guild.id} AND channel_id={channel.id}")
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_thread"), description=translation.get_translation(ctx.user.id, "auto_thread_removed", channel=channel.mention), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)

    @autoThreadsGroup.command(name="list", description="List all auto threads in the guild")
    async def list(self, ctx):
        # List all auto threads in the guild
        logger.log(f"Listing auto threads in {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        threads = database.execute_read_query(f"SELECT channel_id, thread_title FROM auto_threads WHERE guild_id={ctx.guild.id}")
        if not threads:
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_thread"), description=translation.get_translation(ctx.user.id, "no_auto_threads"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        thread_mentions = []
        for thread in threads:
            thread_mentions.append(f"<#{thread[0]}>" + " - " + thread[1])
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_thread"), description=translation.get_translation(ctx.user.id, "auto_threads_list", threads=", \n".join(thread_mentions)), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)


    ######################################################
    # Welcome Messages
    ######################################################

    welcomeGroup = SlashCommandGroup(name="welcome", description="Manage the bot's settings", contexts=[ict.guild], default_member_permissions=discord.Permissions(administrator=True))

    @welcomeGroup.command(name="set", description="Set the welcome message for the guild")
    async def set(self, ctx, title: str, message: str, channel: discord.TextChannel):
        # Set the welcome message for the guild
        logger.log(f"Setting welcome message in {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        # Use parameterized queries to prevent SQL injection and handle special characters
        database.execute_query(
            "INSERT INTO welcome_messages (guild_id, title, message) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE title=%s, message=%s",
            (ctx.guild.id, title, message, title, message)
        )
        database.execute_query(
            "INSERT INTO welcome_channels (guild_id, channel_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE channel_id=%s",
            (ctx.guild.id, channel.id, channel.id)
        )
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "welcome_message_title"), description=translation.get_translation(ctx.user.id, "welcome_message_set", message=message, channel=channel.mention), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)

    @welcomeGroup.command(name="remove", description="Remove the welcome message for the guild")
    async def remove(self, ctx):
        # Remove the welcome message for the guild
        logger.log(f"Removing welcome message in {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        database.execute_query(f"DELETE FROM welcome_messages WHERE guild_id={ctx.guild.id}")
        database.execute_query(f"DELETE FROM welcome_channels WHERE guild_id={ctx.guild.id}")
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "welcome_message_title"), description=translation.get_translation(ctx.user.id, "welcome_message_removed"), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)

    @welcomeGroup.command(name="test", description="Test the welcome message for the guild")
    async def test(self, ctx):
        # Test the welcome message for the guild
        logger.log(f"Testing welcome message in {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        data = database.execute_read_query(f"SELECT * FROM welcome_messages WHERE guild_id = {ctx.guild.id}")
        if not data:
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "welcome_message_title"), description=translation.get_translation(ctx.user.id, "welcome_message_not_set"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        welcomeMessage = data[0][1]
        welcomeMessage = welcomeMessage.replace("{user}", ctx.author.mention)
        welcomeMessage = welcomeMessage.replace("{guild}", ctx.guild.name)
        welcomeTitle = data[0][2]
        channel = database.execute_read_query(f"SELECT * FROM welcome_channels WHERE guild_id = {ctx.guild.id}")
        channel = ctx.guild.get_channel(int(channel[0][1]))
        embed = discord.Embed(title=welcomeTitle, description=welcomeMessage, color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")

        await channel.send(embed=embed)

    @welcomeGroup.command(name="info", description="Get the welcome message for the guild")
    async def info(self, ctx):
        # Get the welcome message for the guild
        logger.log(f"Getting welcome message in {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        data = database.execute_read_query(f"SELECT * FROM welcome_messages WHERE guild_id = {ctx.guild.id}")
        if not data:
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "welcome_message_title"), description=translation.get_translation(ctx.user.id, "welcome_message_not_set"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        welcomeMessage = data[0][1]
        welcomeMessage = welcomeMessage.replace("{user}", ctx.author.mention)
        welcomeMessage = welcomeMessage.replace("{guild}", ctx.guild.name)
        welcomeTitle = data[0][2]
        channel = database.execute_read_query(f"SELECT * FROM welcome_channels WHERE guild_id = {ctx.guild.id}")
        channel = ctx.guild.get_channel(int(channel[0][1]))
        embed = discord.Embed(title=welcomeTitle, description=welcomeMessage, color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)


    ######################################################
    # Auto Reactions
    ######################################################

    autoReactionsGroup = SlashCommandGroup(name="auto_reactions", description="Manage the bot's settings", contexts=[ict.guild], default_member_permissions=discord.Permissions(administrator=True))

    @autoReactionsGroup.command(name="add", description="Add an auto reaction to the guild")
    async def add(self, ctx, channel: discord.TextChannel, emoji: str):
        emoji = emoji.replace(" ", "")
        if ":" not in emoji and em.is_emoji(emoji[1:]):
            emoji = emoji[:1]
            emoji = em.demojize(emoji)
        elif ":" in emoji:
            emoji = "<"+emoji.split("<")[1]
            name = emoji.split(":")[1]
            emoji = discord.utils.get(ctx.guild.emojis, name=name)
            if not emoji:
                embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_reaction"), description=translation.get_translation(ctx.user.id, "auto_reaction_invalid_emoji"), color=discord.Color.red())
                embed.set_footer(text="Made with ❤ by the AutoVox team")
                await ctx.response.send_message(embed=embed)
                return
            emoji = name
        else:
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_reaction"), description=translation.get_translation(ctx.user.id, "auto_reaction_invalid_emoji"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return


        # Check if the emoji is already an auto reaction in that channel
        if database.execute_read_query(f"SELECT * FROM auto_reactions WHERE guild_id={ctx.guild.id} AND channel_id={channel.id} AND reaction='{emoji}'"):
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_reaction"), description=translation.get_translation(ctx.user.id, "auto_reaction_already_added"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        # Check if the auto reaction limit has been reached
        if len(database.execute_read_query(f"SELECT * FROM auto_reactions WHERE guild_id={ctx.guild.id}")) >= config.load_value("auto_reactions_limit"):
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_reactions"), description=translation.get_translation(ctx.user.id, "auto_reactions_limit_reached", limit=config.load_value("auto_reactions_limit")), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        # Check if the Channel is a Text Channel
        if not channel.type == discord.ChannelType.text:
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_reaction"), description=translation.get_translation(ctx.user.id, "auto_reaction_not_text_channel"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        # Add an auto reaction to the guild
        logger.log(f"Adding auto reaction {channel.name}({channel.id}) to {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        # Use parameterized queries to prevent SQL injection and handle special characters
        database.execute_query(
            "INSERT INTO auto_reactions (guild_id, channel_id, reaction) VALUES (%s, %s, %s)",
            (ctx.guild.id, channel.id, emoji)
        )
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_reaction"), description=translation.get_translation(ctx.user.id, "auto_reaction_added", channel=channel.mention, emoji=emoji), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")

        await ctx.response.send_message(embed=embed)

    @autoReactionsGroup.command(name="remove", description="Remove an auto reaction from the guild")
    async def remove(self, ctx, channel: discord.TextChannel):
        # Check if the channel is not an auto reaction
        if not database.execute_read_query(f"SELECT * FROM auto_reactions WHERE guild_id={ctx.guild.id} AND channel_id={channel.id}"):
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_reaction"), description=translation.get_translation(ctx.user.id, "auto_reaction_not_added", channel=channel.mention), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        # Remove an auto reaction from the guild
        logger.log(f"Removing auto reaction {channel.name}({channel.id}) from {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        database.execute_query(f"DELETE FROM auto_reactions WHERE guild_id={ctx.guild.id} AND channel_id={channel.id}")
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_reaction"), description=translation.get_translation(ctx.user.id, "auto_reaction_removed", channel=channel.mention), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)

    @autoReactionsGroup.command(name="list", description="List all auto reactions in the guild")
    async def list(self, ctx):
        # List all auto reactions in the guild
        logger.log(f"Listing auto reactions in {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        reactions = database.execute_read_query(f"SELECT channel_id, reaction FROM auto_reactions WHERE guild_id={ctx.guild.id}")
        if not reactions:
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_reaction"), description=translation.get_translation(ctx.user.id, "no_auto_reactions"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        reaction_mentions = []
        for reaction in reactions:
            if em.is_emoji(em.emojize(reaction[1])):
                reaction_mentions.append(f"<#{reaction[0]}>" + " - " + em.emojize(reaction[1]))
            else:
                emoji = discord.utils.get(ctx.guild.emojis, name=reaction[1])
                if emoji:
                    reaction_mentions.append(f"<#{reaction[0]}>" + " - " + str(emoji))
                else:
                    reaction_mentions.append(f"<#{reaction[0]}>" + " - " + reaction[1])

        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_reaction"), description=translation.get_translation(ctx.user.id, "auto_reactions_list", reactions="\n".join(reaction_mentions)), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(Settings(bot))