import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, Option
from discord import InteractionContextType as ict

import time as tm
import asyncio

import os
import requests

import log_helper

import database

logger = log_helper.Logger("StandardRoles")

class StandardRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    def on_ready(self):
        self.kuma.start()

    @tasks.loop(seconds=60)
    async def kuma(self):
        requests.get(os.getenv("KUMA_STANDARD_ROLES_URL"))


    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Get the guild's standard roles
        standardRoles = database.execute_read_query(f"SELECT * FROM standard_roles WHERE guild_id = {member.guild.id}")
        if not standardRoles:
            return
        # load all standard roles for the guild
        standardRoles = [role[1] for role in standardRoles]
        guild = member.guild
        for role in guild.roles:
            if role.id in standardRoles:
                await member.add_roles(role)
                logger.log(f"Added role {role.name}({role.id}) to {member.name}({member.id})")
        logger.log(f"Added standard roles to {member.name}({member.id})", log_helper.LogTypes.INFO)


def setup(bot):
    bot.add_cog(StandardRoles(bot))