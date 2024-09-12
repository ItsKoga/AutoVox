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

logger = log_helper.Logger("Advertise")


class Advertise(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="invite", description="Get the invite link for the bot")
    async def invite(self, ctx):
        invite_link = config.load_value("invite_link")

        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "invite_title"), description=translation.get_translation(ctx.user.id, "invite_description").format(invite_link=invite_link), color=discord.Color.purple())
        embed.set_footer(text="Made with ❤ by the AutoVox team")

        await ctx.response.send_message(embed=embed)


    @slash_command(name="support", description="Get the support server link for the bot")
    async def support(self, ctx):
        support_link = config.load_value("discord_link")

        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "support_title"), description=translation.get_translation(ctx.user.id, "support_description").format(discord_link=support_link), color=discord.Color.purple())
        embed.set_footer(text="Made with ❤ by the AutoVox team")

        await ctx.response.send_message(embed=embed)

    @slash_command(name="server", description="Get the server link for the bot")
    async def server(self, ctx):
        support_link = config.load_value("discord_link")

        embed = discord.Embed(title=translation.get_translation(ctx.user.id, "server_title"), description=translation.get_translation(ctx.user.id, "server_description").format(discord_link=support_link), color=discord.Color.purple())
        embed.set_footer(text="Made with ❤ by the AutoVox team")

        await ctx.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(Advertise(bot))