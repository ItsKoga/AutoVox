import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, Option
from discord import InteractionContextType as ict

import time as tm
import asyncio

import os

import log_helper

import database

log = log_helper.create("StandardRoles")


class StandardRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_join(self, member):
        # When a member joins the guild
        log(f"Member joined: {member.name}({member.id}) on {member.guild.name}({member.guild.id})", log_helper.LogTypes.INFO)
        # Get the guild's standard roles
        standardRoles = database.execute_read_query(f"SELECT * FROM standard_roles WHERE guild_id = {member.guild.id}")
        # load all standard roles for the guild
        standardRoles = [role[0] for role in standardRoles]
        guild = member.guild
        for role in guild.roles:
            if role.id in standardRoles:
                await member.add_roles(role)
                log(f"Added role {role.name}({role.id}) to {member.name}({member.id})", log_helper.LogTypes.INFO)
        log(f"Added standard roles to {member.name}({member.id})", log_helper.LogTypes.INFO)


def setup(bot):
    bot.add_cog(StandardRoles(bot))