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

logger = log_helper.Logger("AutoThread")


class AutoThread(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.kuma.start()

    @tasks.loop(seconds=60)
    async def kuma(self):
        requests.get(os.getenv("KUMA_AUTO_THREAD_URL"))

    @commands.Cog.listener()
    async def on_message(self, message):
        autoThreads = database.execute_read_query(f"SELECT * FROM auto_threads WHERE guild_id = {message.guild.id}")

        if not autoThreads:
            return

        # Check if the Channel is an AutoThread
        if message.channel.id in [int(thread[1]) for thread in autoThreads]:
            # Check if the message is from the bot
            if message.author.id == self.bot.user.id:
                return

            # Get the AutoThread
            autoThread = [thread for thread in autoThreads if thread[1] == message.channel.id][0]

            threadTitle = autoThread[2]

            # Replace the Placeholder with the User's Name
            if "{user}" in threadTitle:
                threadTitle = threadTitle.replace("{user}", message.author.name)

            # Create the Thread
            thread = await message.create_thread(name=threadTitle)

            logger.log(f"Created thread {thread.id} in {message.guild.id}")


def setup(bot):
    bot.add_cog(AutoThread(bot))