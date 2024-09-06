import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, Option, SlashCommandGroup
from discord import InteractionContextType as ict

import time as tm
import asyncio

import os

import log_helper

import translation

import database

logger = log_helper.Logger("Settings")


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    stardardRolesGroup = SlashCommandGroup(name="standard_roles", description="Manage the bot's settings", contexts=[ict.guild], default_member_permissions=discord.Permissions(administrator=True))

    ######################################################
    # Standard Roles
    ######################################################
    @stardardRolesGroup.command(name="add", description="Add a standard role to the guild")
    async def add(self, ctx, role: discord.Role):
        # Add a standard role to the guild
        logger.log(f"Adding standard role {role.name}({role.id}) to {ctx.guild.name}({ctx.guild.id}) by {ctx.user.name}({ctx.user.id})", log_helper.LogTypes.INFO)
        database.execute_query(f"INSERT INTO standard_roles (guild_id, role_id) VALUES ({ctx.guild.id}, {role.id})")
        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "standard_role_added_title"), description=translation.get_translation(ctx.user.id, "standard_role_added", role=role.mention), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)

    @stardardRolesGroup.command(name="remove", description="Remove a standard role from the guild")
    async def remove(self, ctx, role: discord.Role):
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





def setup(bot):
    bot.add_cog(Settings(bot))