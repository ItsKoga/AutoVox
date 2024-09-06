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


def setup(bot):
    bot.add_cog(Settings(bot))