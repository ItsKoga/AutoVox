import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, Option, SlashCommandGroup
from discord import InteractionContextType as ict

import time as tm
import asyncio

import os
import requests

import log_helper

import translation

import config

import database

logger = log_helper.Logger("VoiceSettings")


class VoiceSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def on_ready(self):
        self.kuma.start()

    @tasks.loop(seconds=60)
    async def kuma(self):
        requests.get(os.getenv("KUMA_VOICE_SETTINGS_URL"))


    voiceGroup = SlashCommandGroup(name="channel", description="Manage your channel settings")

    @voiceGroup.command(name="name", description="Change the name of your channel")
    async def voice_name(self, ctx, name: str):
        channel = database.execute_read_query(f"SELECT * FROM custom_channels WHERE owner_id = {ctx.author.id} AND guild_id = {ctx.guild.id}")
        if not channel:
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "channel_title"), description=translation.get_translation(ctx.author.id, "channel_not_found"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        
        if len(name) > config.load_value("channel_name_limit"):
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "channel_title"), description=translation.get_translation(ctx.author.id, "channel_name_limit", limit=config.load_value("channel_name_limit")), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        
        if len(name) < 1:
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "channel_title"), description=translation.get_translation(ctx.author.id, "channel_name_empty"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return

        channel = ctx.guild.get_channel(int(channel[0][1]))
        await channel.edit(name=name)

        embed = discord.Embed(title=translation.get_translation(ctx.author.id, "channel_title"), description=translation.get_translation(ctx.author.id, "channel_name_success", name=name), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)
        logger.log(f"User {ctx.author.id} changed their channel({channel.id}) name to {name}", log_helper.LogTypes.USER_ACTION)


    @voiceGroup.command(name="limit", description="Change the user limit of your channel")
    async def voice_limit(self, ctx, limit: int):
        channel = database.execute_read_query(f"SELECT * FROM custom_channels WHERE owner_id = {ctx.author.id} AND guild_id = {ctx.guild.id}")
        if not channel:
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "channel_title"), description=translation.get_translation(ctx.author.id, "channel_not_found"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        
        if limit > config.load_value("channel_user_limit"):
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "channel_title"), description=translation.get_translation(ctx.author.id, "channel_user_limit", limit=config.load_value("channel_user_limit")), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        
        if limit < 0:
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "channel_title"), description=translation.get_translation(ctx.author.id, "channel_user_limit_negative"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return

        channel = ctx.guild.get_channel(int(channel[0][1]))
        await channel.edit(user_limit=limit)

        embed = discord.Embed(title=translation.get_translation(ctx.author.id, "channel_title"), description=translation.get_translation(ctx.author.id, "channel_limit_success", limit=limit), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)
        logger.log(f"User {ctx.author.id} changed their channel({channel.id}) user limit to {limit}", log_helper.LogTypes.USER_ACTION)


    @voiceGroup.command(name="lock", description="Lock your channel")
    async def voice_lock(self, ctx):
        channel = database.execute_read_query(f"SELECT * FROM custom_channels WHERE owner_id = {ctx.author.id} AND guild_id = {ctx.guild.id}")
        if not channel:
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "channel_title"), description=translation.get_translation(ctx.author.id, "channel_not_found"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return

        channel = ctx.guild.get_channel(int(channel[0][1]))
        # Check if the channel is already locked
        if channel.overwrites_for(ctx.guild.default_role).connect == False:
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "channel_title"), description=translation.get_translation(ctx.author.id, "channel_lock_already"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return

        # Create a Join Channel obove the user's channel
        joinChannel = await ctx.guild.create_voice_channel(name=f"⇩ {ctx.user.name}", category=channel.category, position=channel.position-1)
        database.execute_query(f"INSERT INTO join_channels (owner_id, channel_id, guild_id) VALUES ({ctx.author.id}, {joinChannel.id}, {ctx.guild.id})")

        await channel.set_permissions(ctx.guild.default_role, connect=False)

        embed = discord.Embed(title=translation.get_translation(ctx.author.id, "channel_title"), description=translation.get_translation(ctx.author.id, "channel_lock_success"), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)


    @voiceGroup.command(name="unlock", description="Unlock your channel")
    async def voice_unlock(self, ctx):
        channel = database.execute_read_query(f"SELECT * FROM custom_channels WHERE owner_id = {ctx.author.id} AND guild_id = {ctx.guild.id}")
        if not channel:
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "channel_title"), description=translation.get_translation(ctx.author.id, "channel_not_found"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return

        channel = ctx.guild.get_channel(int(channel[0][1]))
        # Check if the channel is already unlocked
        if channel.overwrites_for(ctx.guild.default_role).connect == None:
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "channel_title"), description=translation.get_translation(ctx.author.id, "channel_unlock_already"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return

        # Remove the Join Channel
        joinChannel = database.execute_read_query(f"SELECT * FROM join_channels WHERE owner_id = {ctx.author.id} AND guild_id = {ctx.guild.id}")
        joinChannel = ctx.guild.get_channel(int(joinChannel[0][1]))
        await joinChannel.delete()
        database.execute_query(f"DELETE FROM join_channels WHERE owner_id = {ctx.author.id} AND guild_id = {ctx.guild.id}")

        await channel.set_permissions(ctx.guild.default_role, connect=None)

        embed = discord.Embed(title=translation.get_translation(ctx.author.id, "channel_title"), description=translation.get_translation(ctx.author.id, "channel_unlock_success"), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)



def setup(bot):
    bot.add_cog(VoiceSettings(bot))