import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import asyncio
import os
import sys	
import subprocess

import log_helper
from log_helper import LogTypes

import config

# Initialize bot with all intents
bot = commands.Bot(intents=discord.Intents.all())
log = log_helper.create("main")

# Bot event handlers
@bot.event
async def on_ready():
    # Set bot's presence
    await bot.change_presence(activity=discord.Game(name="AutoVox"), status=discord.Status.online)
    log("Bot is Online!", LogTypes.SUCCESS)


@bot.event
async def on_command_error(ctx, error):
    # Global error handler for commands
    embed = discord.Embed(title="An error occurred", description=f"```{error}```", color=discord.Color.red())
    embed.add_field(name="Report", value="Please report this error to the AutoVox team. You can join the support server [here](https://discord.gg/8HbjJBGWBd)")
    embed.set_footer(text="Made with ❤ by the AutoVox team")
    ctx.response.send_message(f"An error occurred: {error}", LogTypes.ERROR)

    log(f"An error occurred: {error}", LogTypes.ERROR)


@bot.event
async def on_guild_join(guild):
    # When the bot joins a guild
    log(f"Joined guild: {guild.name}, {guild.id}", LogTypes.INFO)

@bot.event
async def on_guild_remove(guild):
    # When the bot leaves a guild
    log(f"Left guild: {guild.name}, {guild.id}", LogTypes.INFO)

@bot.event
async def on_interaction(interaction):
    # When an interaction is received
    log(f"Interaction received: {interaction}", LogTypes.INFO)


@bot.event
async def restart(ctx): # can be triggered in a cog by self.bot.dispatch("restart")
    # Restart the bot
    log("Restarting...", LogTypes.SYSTEM)
    await ctx.send("Restarting...")
    await bot.close()
    os.execv(sys.executable, ['python'] + sys.argv)



# Load extensions (cogs) from the 'cogs' directory
async def load_extensions():
    log("Loading Cogs...", LogTypes.SYSTEM)
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            cog_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(cog_name)
                log(f"Loaded {cog_name}", LogTypes.SUCCESS)
            except Exception as e:
                log(f"Failed to load {cog_name}: {e}", LogTypes.ERROR)



# Check for updates on GitHub
@tasks.loop(minutes=30)
async def check_for_updates():
    log("Checking for updates...", LogTypes.SYSTEM)
    result = subprocess.run(["git", "fetch", config.load_value("repo_url")], capture_output=True, text=True)
    if result.returncode != 0:
        log(f"Failed to fetch updates: {result.stderr}", LogTypes.ERROR)
        return

    result = subprocess.run(["git", "status", "-uno"], capture_output=True, text=True)
    if "Your branch is behind" in result.stdout:
        log("Updates found. Updating...", LogTypes.SYSTEM)
        await update_and_restart()

async def update_and_restart():
    log("Shutting down for update...", LogTypes.SYSTEM)
    await bot.close()

    result = subprocess.run(["git", "pull", config.load_value("repo_url")], capture_output=True, text=True)
    if result.returncode != 0:
        log(f"Failed to pull updates: {result.stderr}", LogTypes.ERROR)
        return

    log("Restarting with updates...", LogTypes.SYSTEM)
    os.execv(sys.executable, ['python'] + sys.argv)

# Main entry point
if __name__ == "__main__":
    load_dotenv()
    try:
        asyncio.run(load_extensions())
        log("Starting Bot...", LogTypes.SYSTEM)
        TOKEN = os.getenv('TOKEN')  # Ensure that the TOKEN is loaded from the environment variables
        asyncio.run(bot.start(TOKEN))
    except KeyboardInterrupt:
        log("Shutdown signal received", LogTypes.SYSTEM)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(bot.close())  # Gracefully close the bot
        log("Bot has been gracefully shutdown.", LogTypes.SUCCESS)
    except Exception as e:
        log(f"An error occurred: {e}", LogTypes.ERROR)
    finally:
        loop.close()  # Close the asyncio loop