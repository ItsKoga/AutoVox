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

logger = log_helper.Logger("Whitelist")


class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    whitelistGroup = SlashCommandGroup(name="whitelist", description="Manage your whitelist")

    @whitelistGroup.command(name="add", description="Add a user to your whitelist")
    async def whitelist_add(self, ctx, user: discord.User):
        whitelist = database.execute_read_query(f"SELECT * FROM whitelist WHERE user_id = {ctx.author.id} AND guild_id = {ctx.guild.id}")
        whitelist = [item[2] for item in whitelist]

        if user.id == ctx.author.id:
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "whitelist_title"), description=translation.get_translation(ctx.author.id, "whitelist_add_self"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        
        if user.bot:
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "whitelist_title"), description=translation.get_translation(ctx.author.id, "whitelist_add_bot", user=user.mention), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return

        if user.id in whitelist:
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "whitelist_title"), description=translation.get_translation(ctx.author.id, "whitelist_add_already", user=user.mention), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        
        if len(whitelist) > config.load_value("whitelist_limit"):
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "whitelist_title"), description=translation.get_translation(ctx.author.id, "whitelist_add_limit", limit=config.load_value("whitelist_limit")), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        
        database.execute_query(f"INSERT INTO whitelist (guild_id, user_id, whitelisted_user_id) VALUES ({ctx.guild.id}, {ctx.author.id}, {user.id})")
        embed = discord.Embed(title=translation.get_translation(ctx.author.id, "whitelist_title"), description=translation.get_translation(ctx.author.id, "whitelist_add_success", user=user.mention), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)


    @whitelistGroup.command(name="remove", description="Remove a user from your whitelist")
    async def whitelist_remove(self, ctx, user: discord.User):
        whitelist = database.execute_read_query(f"SELECT * FROM whitelist WHERE user_id = {ctx.author.id} AND guild_id = {ctx.guild.id}")
        whitelist = [item[2] for item in whitelist]

        if user.id not in whitelist:
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "whitelist_title"), description=translation.get_translation(ctx.author.id, "whitelist_remove_not_found", user=user.mention), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        
        database.execute_query(f"DELETE FROM whitelist WHERE guild_id = {ctx.guild.id} AND user_id = {user.id} AND whitelisted_user_id = {user.id}")
        embed = discord.Embed(title=translation.get_translation(ctx.author.id, "whitelist_title"), description=translation.get_translation(ctx.author.id, "whitelist_remove_success", user=user.mention), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)


    @whitelistGroup.command(name="list", description="List all users in your whitelist")
    async def whitelist_list(self, ctx):
        whitelist = database.execute_read_query(f"SELECT * FROM whitelist WHERE user_id = {ctx.author.id} AND guild_id = {ctx.guild.id}")
        whitelist = [item[2] for item in whitelist]

        if not whitelist:
            embed = discord.Embed(title=translation.get_translation(ctx.author.id, "whitelist_title"), description=translation.get_translation(ctx.author.id, "whitelist_list_empty"), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await ctx.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(title=translation.get_translation(ctx.author.id, "whitelist_title"), description=translation.get_translation(ctx.author.id, "whitelist_list", whitelist="\n".join([f"<@{item}>" for item in whitelist])), color=discord.Color.green())
        embed.set_footer(text="Made with ❤ by the AutoVox team")
        await ctx.response.send_message(embed=embed)




def setup(bot):
    bot.add_cog(Whitelist(bot))