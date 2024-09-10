import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, Option, SlashCommandGroup
from discord import InteractionContextType as ict

import time as tm
import asyncio

import os

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
        # Check for invalid title
        if "'" in title:
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_thread"), description=translation.get_translation(ctx.user.id, "auto_thread_invalid_title", title=title), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        # Add an auto thread to the guild
        logger.log(f"Adding auto thread {channel.name}({channel.id}) to {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        database.execute_query(f"INSERT INTO auto_threads (guild_id, channel_id, thread_title) VALUES ({ctx.guild.id}, {channel.id}, '{title}')")
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
            embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_threads"), description=translation.get_translation(ctx.user.id, "no_auto_threads"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        thread_mentions = []
        for thread in threads:
            thread_mentions.append(f"<#{thread[0]}>" + " - " + thread[1])
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "auto_threads"), description=translation.get_translation(ctx.user.id, "auto_threads_list", threads=", \n".join(thread_mentions)), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(Settings(bot))