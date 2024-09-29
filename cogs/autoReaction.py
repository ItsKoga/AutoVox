import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, Option, SlashCommandGroup
from discord import InteractionContextType as ict

import time as tm
import asyncio

import os
import requests

import emoji as em

import log_helper

import translation

import config

import database

logger = log_helper.Logger("AutoReaction")


class AutoReaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def on_ready(self):
        self.kuma.start()

    @tasks.loop(seconds=60)
    async def kuma(self):
        requests.get(os.getenv("KUMA_AUTO_REACTION_URL"))

    @commands.Cog.listener()
    async def on_message(self, message):
        autoReaction = database.execute_read_query(f"SELECT * FROM auto_reactions WHERE guild_id = {message.guild.id}")

        if not autoReaction:
            return
        
        # Check if the Channel is in a Thread
        if message.thread:
            return


        if message.channel.id in [int(reaction[1]) for reaction in autoReaction]:
            if message.author.id == self.bot.user.id:
                return

            autoReactions = [reaction for reaction in autoReaction if reaction[1] == message.channel.id]

            for autoReaction in autoReactions:
                reactionEmoji = autoReaction[2]

                if em.is_emoji(em.emojize(reactionEmoji)):
                    await message.add_reaction(em.emojize(reactionEmoji))
                else:
                    reactionEmoji = discord.utils.get(message.guild.emojis, name=reactionEmoji)
                    if reactionEmoji:
                        await message.add_reaction(reactionEmoji)

            logger.log(f"Added reactions to message {message.id} in {message.guild.id}")


def setup(bot):
    bot.add_cog(AutoReaction(bot))