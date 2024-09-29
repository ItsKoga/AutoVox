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

logger = log_helper.Logger("Help")


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    def on_ready(self):
        self.kuma.start()

    @tasks.loop(seconds=60)
    async def kuma(self):
        requests.get(os.getenv("KUMA_HELP_URL"))

    @slash_command(name="help", description="Shows the help menu")
    async def help(self, ctx):
        embed = discord.Embed(title=translation.get_translation(ctx.author.id, "help_title"), description=translation.get_translation(ctx.author.id, "help_description", documentation_link=config.load_value("website_url")+"/docs", discord_link=config.load_value("discord_link")), color=0x9c59b6)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Made with ❤ by the AutoVox team")

        class MyView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.timeout = 300

                wiki_button = discord.ui.Button(label=translation.get_translation(ctx.author.id, "wiki_button"), style=discord.ButtonStyle.link, url=config.load_value("website_url")+"/docs")
                self.add_item(wiki_button)

                discord_button = discord.ui.Button(label=translation.get_translation(ctx.author.id, "support_title"), style=discord.ButtonStyle.link, url=config.load_value("discord_link"))
                self.add_item(discord_button)

            def on_timeout(self):
                self.disable_all_items()

        await ctx.response.send_message(embed=embed, view=MyView())


def setup(bot):
    bot.add_cog(Help(bot))