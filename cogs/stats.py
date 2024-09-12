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

logger = log_helper.Logger("Stats")


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_stats = None

    class BotStats(commands.Cog):
        def __init__(self, bot, amountServers, amountCustomChannels, amountJoinChannels, autoThreads, whitelistEntries):
            self.bot = bot
            self.amountServers = amountServers
            self.amountCustomChannels = amountCustomChannels
            self.amountJoinChannels = amountJoinChannels
            self.autoThreads = autoThreads
            self.whitelistEntries = whitelistEntries

    def update_stats(self):
        try:
            amountServers = len(self.bot.guilds)
            amountCustomChannels = len(database.execute_read_query("SELECT * FROM custom_channels"))
            amountJoinChannels = len(database.execute_read_query("SELECT * FROM join_channels"))
            autoThreads = len(database.execute_read_query("SELECT * FROM auto_threads"))
            whitelistEntries = len(database.execute_read_query("SELECT * FROM whitelist"))

            self.bot_stats = self.BotStats(self.bot, amountServers, amountCustomChannels, amountJoinChannels, autoThreads, whitelistEntries)
        except Exception as e:
            logger.log(f"Failed to update stats: {e}", log_helper.LogTypes.ERROR)

        
    @tasks.loop(seconds=300)
    async def update_stats_loop(self):
        self.update_stats()

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_stats_loop.start()
        

    
    @slash_command(name="stats", description="Get the stats of the bot")
    async def stats(self, ctx):
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "stats_title"), description=translation.get_translation(ctx.user.id, "stats_description").format(amountServers=self.bot_stats.amountServers, amountCustomChannels=self.bot_stats.amountCustomChannels, amountJoinChannels=self.bot_stats.amountJoinChannels, amountAutoThreads=self.bot_stats.autoThreads, amountWhitelist=self.bot_stats.whitelistEntries), color=discord.Color.purple())
        embed.set_footer(text="Made with ❤ by the AutoVox team")

        await ctx.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(Stats(bot))