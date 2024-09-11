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

logger = log_helper.Logger("Welcome")


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # When a member joins a guild
        logger.log(f"Member joined: {member.name}, {member.id} on {member.guild.name}, {member.guild.id}", log_helper.LogTypes.INFO)
        data = database.execute_read_query(f"SELECT * FROM welcome_messages WHERE guild_id = {member.guild.id}")
        if not welcomeMessage:
            return

        welcomeMessage = data[0][1]
        welcomeMessage = welcomeMessage.replace("{user}", member.mention)
        welcomeMessage = welcomeMessage.replace("{guild}", member.guild.name)

        welcomeTitle = data[0][2]

        channel = database.execute_read_query(f"SELECT * FROM welcome_channels WHERE guild_id = {member.guild.id}")
        
        channel = member.guild.get_channel(int(channel[0][1]))
        
        embed = discord.Embed(title=welcomeTitle, description=welcomeMessage, color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")

        await channel.send(embed=embed)
        logger.log(f"Sent welcome message to {member.name} in {member.guild.name}", log_helper.LogTypes.INFO)
            


def setup(bot):
    bot.add_cog(Welcome(bot))