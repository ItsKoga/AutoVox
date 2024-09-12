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

logger = log_helper.Logger("Admin")


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    admin_group = SlashCommandGroup(name="admin", description="Admin commands", default_member_permissions=discord.Permissions(administrator=True), guild_ids=[config.load_value("guild_id")])

    # No Translation needed, as this is only for the bot admins

    @admin_group.command(name="guilds", description="Get the guilds the bot is in")
    async def guilds(self, ctx):
        guilds = self.bot.guilds

        embed = discord.Embed(title="Guilds", description=f"The bot is in {len(guilds)} guilds", color=0x00ff00)
        embed.set_footer("Made with ❤ by the AutoVox team")

        await ctx.response.send_message(embed=embed)

    @admin_group.command(name="leave", description="Leave a guild")
    async def leave(self, ctx, guild_id: int):
        guild = self.bot.get_guild(guild_id)

        if guild is None:
            await ctx.response.send_message("Guild not found")
            return

        class view(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.timeout = 20

            async def on_timeout(self):
                await self.message.edit(view=None)

            @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
            async def yes(self, button, interaction):
                await guild.leave()
                self.disable_all_items()
                await interaction.edit_original_response(content="Left guild", view=self)

            @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
            async def no(self, button, interaction):
                self.disable_all_items()
                await interaction.edit_original_response(content="Did not leave guild", view=self)

        await ctx.response.send_message("Are you sure you want to leave this guild?", view=view())


    @admin_group.command(name="guild", description="Get the guild")
    async def guild(self, ctx, guild_id: int):
        guild = self.bot.get_guild(guild_id)

        if guild is None:
            await ctx.response.send_message("Guild not found")
            return

        embed = discord.Embed(title="Guild", description=f"Name: {guild.name}\nID: {guild.id}\nOwner: {guild.owner.mention}({guild.owner.id})\nMembers: {guild.member_count}", color=0x00ff00)
        embed.set_footer("Made with ❤ by the AutoVox team")

        await ctx.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(Admin(bot))