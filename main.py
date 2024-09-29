import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import asyncio
import os
import sys	

from mysql.connector import Error

import log_helper
from log_helper import LogTypes

import database

import config
import translation

# Initialize bot with all intents
bot = commands.Bot(intents=discord.Intents.all())
logger = log_helper.Logger("Main")

# Bot event handlers
@bot.event
async def on_ready():
    # Set bot's presence
    await bot.change_presence(activity=discord.Game(name="AutoVox"), status=discord.Status.online)
    logger.log("Bot is online!", LogTypes.SUCCESS)


@bot.event
async def on_command_error(ctx, error):
    # Global error handler for commands
    embed = discord.Embed(title=translation.get_translation(ctx.author.id, "error_report_title"), description=translation.get_translation(ctx.author.id, "error_report", command=ctx.command.name), color=discord.Color.red())
    embed.set_footer(text="Made with ❤ by the AutoVox team")
    await ctx.response.send_message(f"An error occurred: {error}", LogTypes.ERROR)

    logger.log(f"An error occurred: {error}", LogTypes.ERROR)


@bot.event
async def on_guild_join(guild):
    # When the bot joins a guild
    logger.log(f"Joined guild: {guild.name}, {guild.id}", LogTypes.INFO)

    ownGuild = bot.get_guild(config.load_value("guild_id"))

    channel = ownGuild.get_channel(config.load_value("log_channel_id"))

    embed = discord.Embed(title="Joined Guild", description=f"{guild.name}, {guild.id} members: {guild.member_count}", color=discord.Color.green())
    embed.set_footer(text="Made with ❤ by the AutoVox team")

    await channel.send(embed=embed)


@bot.event
async def on_guild_remove(guild):
    # When the bot leaves a guild
    logger.log(f"Left guild: {guild.name}, {guild.id}", LogTypes.INFO)

    ownGuild = bot.get_guild(config.load_value("guild_id"))

    channel = ownGuild.get_channel(config.load_value("log_channel_id"))

    embed = discord.Embed(title="Left Guild", description=f"{guild.name}, {guild.id}", color=discord.Color.red())
    embed.set_footer(text="Made with ❤ by the AutoVox team")

    await channel.send(embed=embed)


@bot.event
async def on_interaction(interaction):
    # When an interaction is invoked
    data = interaction.data
    if interaction.type == discord.InteractionType.component:
        await interaction.response.defer()
        return

    name = data["name"]
    option_name = data["options"][0]["name"] if "options" in data else None
    logger.log(f"Interaction invoked by {interaction.user.id}: {name} {option_name}", LogTypes.USER_ACTION)

    # Add the user to the database if they don't exist
    if not database.execute_read_query(f"SELECT * FROM users WHERE id = {interaction.user.id}"):
        database.execute_query(f"INSERT INTO users (id) VALUES ({interaction.user.id})")
        logger.log(f"Added user {interaction.user.name}({interaction.user.id}) to the database", LogTypes.INFO)

    # Check if the interaction is a command
    if interaction.type == discord.InteractionType.application_command:
        # Check if command is registered
        if not bot.get_application_command(name):
            logger.log(f"Command {name} not found", LogTypes.ERROR)
            embed = discord.Embed(title=translation.get_translation(interaction.user.id, "command_not_found_title"), description=translation.get_translation(interaction.user.id, "command_not_found", command=name), color=discord.Color.red())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            await interaction.response.send_message(embed=embed)
            return

        # Process the interaction
        await bot.process_application_commands(interaction)


@bot.event
async def restart(ctx): # can be triggered in a cog by self.bot.dispatch("restart")
    # Restart the bot
    logger.log("Restarting...", LogTypes.SYSTEM)
    await ctx.send("Restarting...")
    await bot.close()
    os.execv(sys.executable, ['python'] + sys.argv)


# Load extensions (cogs) from the 'cogs' directory
async def load_extensions():
    logger.log("Loading Cogs...", LogTypes.SYSTEM)
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            cog_name = f"cogs.{filename[:-3]}"
            try:
                bot.load_extension(cog_name)
                logger.log(f"Loaded {cog_name}", LogTypes.SUCCESS)
            except Exception as e:
                logger.log(f"Failed to load {cog_name}: {e}", LogTypes.ERROR)


async def create_database():
    # Create the database if it doesn't exist
    logger.log("Creating Database...", LogTypes.SYSTEM)
    database.execute_query("CREATE TABLE IF NOT EXISTS standard_roles (guild_id BIGINT, role_id BIGINT)")
    database.execute_query("CREATE TABLE IF NOT EXISTS settings (guild_id BIGINT, setting_name TEXT, setting_value TEXT)")
    database.execute_query("CREATE TABLE IF NOT EXISTS users (id BIGINT, language_code TEXT DEFAULT 'en')")
    database.execute_query("CREATE TABLE IF NOT EXISTS custom_channels (owner_id BIGINT, channel_id BIGINT, guild_id BIGINT)")
    database.execute_query("CREATE TABLE IF NOT EXISTS join_channels (owner_id BIGINT, channel_id BIGINT, guild_id BIGINT)")
    database.execute_query("CREATE TABLE IF NOT EXISTS whitelist (guild_id BIGINT, user_id BIGINT, whitelisted_user_id BIGINT)")
    database.execute_query("CREATE TABLE IF NOT EXISTS auto_threads (guild_id BIGINT, channel_id BIGINT, thread_title TEXT)")
    database.execute_query("CREATE TABLE IF NOT EXISTS welcome_messages (guild_id BIGINT, message TEXT, title TEXT)")
    database.execute_query("CREATE TABLE IF NOT EXISTS welcome_channels (guild_id BIGINT, channel_id BIGINT)")
    database.execute_query("CREATE TABLE IF NOT EXISTS auto_reactions (guild_id BIGINT, channel_id BIGINT, reaction TEXT)")
    database.execute_query("CREATE TABLE IF NOT EXISTS stats (id INT PRIMARY KEY AUTO_INCREMENT, users BIGINT, servers BIGINT, commands BIGINT, time BIGINT)")
    logger.log("Database is ready", LogTypes.SUCCESS)


async def main():
    logger.log("Starting AutoVox...", LogTypes.SYSTEM)
    logger.log("Checking database connection...", LogTypes.SYSTEM)
    check = database.check_database()
    if check == Error:
        logger.log(f"Database connection failed: {check}", LogTypes.ERROR)
        sys.exit(1)
    logger.log("Database connection successful", LogTypes.SUCCESS)
    load_dotenv()
    try:
        await create_database()
        await load_extensions()
        logger.log("Starting Bot...", LogTypes.SYSTEM)
        TOKEN = os.getenv('TOKEN')  # Ensure that the TOKEN is loaded from the environment variables
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        logger.log("Shutdown signal received", LogTypes.SYSTEM)
        await bot.close()  # Gracefully close the bot
        logger.log("Bot has been gracefully shutdown.", LogTypes.SUCCESS)
    except Exception as e:
        logger.log(f"An error occurred: {e}", LogTypes.ERROR)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())