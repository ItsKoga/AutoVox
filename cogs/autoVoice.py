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

logger = log_helper.Logger("AutoVoice")


class AutoVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        # Check all channels in the database and delete them if they don't exist in the guild
        logger.log("Checking all channels in the database", log_helper.LogTypes.INFO)
        customChannels = database.execute_read_query("SELECT * FROM custom_channels")
        joinChannels = database.execute_read_query("SELECT * FROM join_channels")

        guilds = []
        for channel in customChannels:
            if channel[2] not in guilds:
                guilds.append(int(channel[2]))
        for channel in joinChannels:
            if channel[1] not in guilds:
                guilds.append(int(channel[2]))

        # Create a list with all the guild and channel ids
        guildsList = {}
        for guild in guilds:
            guildsList[guild] = {"custom": [], "join": []}
            for channel in customChannels:
                if channel[2] == guild:
                    guildsList[guild]["custom"].append(int(channel[1]))
            for channel in joinChannels:
                if channel[1] == guild:
                    guildsList[guild]["join"].append(int(channel[1]))

        for guildToCheck in guildsList:
            guild = self.bot.get_guild(int(guildToCheck))
            logger.log(f"Checking channels in {guild.name}({guild.id})", log_helper.LogTypes.INFO)
            channels = guild.voice_channels
            channelIds = [channel.id for channel in channels]
            guildToCheck = guildsList[guildToCheck]
            for channel in guildToCheck["custom"]:
                if channel not in channelIds:
                    database.execute_query(f"DELETE FROM custom_channels WHERE channel_id = {channel}")
                    guildToCheck["custom"].remove(channel)
            for channel in guildToCheck["join"]:
                if channel not in channelIds:
                    database.execute_query(f"DELETE FROM join_channels WHERE channel_id = {channel}")
                    guildToCheck["join"].remove(channel)
            guildsList[guild.id] = guildToCheck

            # Change the owner of the Custom Channel if the owner left or deleted the channel if the channel is empty
            customChannelsWithOwners = database.execute_read_query(f"SELECT * FROM custom_channels WHERE guild_id = {guild.id}")
            joinChannelsWithOwners = database.execute_read_query(f"SELECT * FROM join_channels WHERE guild_id = {guild.id}")
            for channelToCheck in customChannelsWithOwners:
                channel = guild.get_channel(int(channelToCheck[1]))
                if len(channel.members) == 0:
                    database.execute_query(f"DELETE FROM custom_channels WHERE channel_id = {channel.id}")
                    await channel.delete()
                    # Check if the owner has a join channel and delete it if it's empty
                    joinChannel = database.execute_read_query(f"SELECT * FROM join_channels WHERE owner_id = {channelToCheck[0]}")
                    if joinChannel:
                        database.execute_query(f"DELETE FROM join_channels WHERE owner_id = {channelToCheck[0]}")
                        joinChannel = guild.get_channel(joinChannel[0][1])
                        await joinChannel.delete()

                else:
                    oldOwner = channelToCheck[0]
                    if oldOwner not in [member.id for member in channel.members]:
                        owner = channel.members[0].id   
                        database.execute_query(f"UPDATE custom_channels SET owner_id = {owner} WHERE channel_id = {channel.id}")
                        for channel in joinChannelsWithOwners:
                            if channel[0] == owner:
                                database.execute_query(f"UPDATE join_channels SET owner_id = {owner} WHERE owner_id = {oldOwner}")
            logger.log(f"Checked channels in {guild.name}({guild.id})", log_helper.LogTypes.INFO)


        logger.log("AutoVoice is Online!", log_helper.LogTypes.SUCCESS)
        


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # When a member joins or leaves a voice channel
        if before.channel == after.channel:
            return
        
        guild = member.guild
        createChannel = int(database.execute_read_query(f"SELECT * FROM settings WHERE guild_id = {member.guild.id} AND setting_name = 'create_channel'")[0][2])
        createChannel = guild.get_channel(createChannel)

        requestChannel = int(database.execute_read_query(f"SELECT * FROM settings WHERE guild_id = {member.guild.id} AND setting_name = 'request_channel'")[0][2])
        requestChannel = guild.get_channel(requestChannel)

        joinChannels = database.execute_read_query(f"SELECT * FROM join_channels WHERE guild_id = {member.guild.id}")
        joinChannels = [channel[1] for channel in joinChannels]

        customChannels = database.execute_read_query(f"SELECT * FROM custom_channels WHERE guild_id = {member.guild.id}")
        customChannelOwners = [int(channel[0]) for channel in customChannels]
        customChannels = [int(channel[1]) for channel in customChannels]

        customCatagory = createChannel.category

        if after.channel == createChannel:
            if member.id in customChannelOwners:
                logger.log(f"User {member.name}({member.id}) joined the create channel in {guild.name}({guild.id}) and has a custom channel", log_helper.LogTypes.INFO)
                customChannel = customChannels[customChannelOwners.index(member.id)]
                customChannel = guild.get_channel(customChannel)
                await member.move_to(customChannel)
                return
            logger.log(f"User {member.name}({member.id}) joined the create channel in {guild.name}({guild.id}) and does not have a custom channel", log_helper.LogTypes.INFO)
            channel = await guild.create_voice_channel(f"Talk {len(customChannels) + 1}", category=customCatagory)
            await member.move_to(channel)
            database.execute_query(f"INSERT INTO custom_channels (owner_id, channel_id, guild_id) VALUES ({member.id}, {channel.id}, {guild.id})")
            logger.log(f"User {member.name}({member.id}) created a custom channel in {guild.name}({guild.id})", log_helper.LogTypes.INFO)
            return
        
        if member.id in customChannelOwners:
            if before.channel == createChannel:
                return
            customChannel = customChannels[customChannelOwners.index(member.id)]
            customChannel = guild.get_channel(customChannel)
            if len(customChannel.members) == 0:
                await customChannel.delete()
                database.execute_query(f"DELETE FROM custom_channels WHERE owner_id = {member.id}")
                joinChannel = database.execute_read_query(f"SELECT * FROM join_channels WHERE owner_id = {member.id} AND guild_id = {guild.id}")
                if joinChannel:
                    joinChannel = guild.get_channel(joinChannel[0][1])
                    await joinChannel.delete()
                logger.log(f"User {member.name}({member.id}) left their custom channel in {guild.name}({guild.id}) and the channel was deleted", log_helper.LogTypes.INFO)
                return
            # Set the channel owner to the first member in the channel
            channelOwner = customChannel.members[0]
            database.execute_query(f"UPDATE custom_channels SET owner_id = {channelOwner.id} WHERE owner_id = {member.id}")
            joinChannel = database.execute_read_query(f"SELECT * FROM join_channels WHERE owner_id = {member.id} AND guild_id = {guild.id}")
            if joinChannel:
                database.execute_query(f"UPDATE join_channels SET owner_id = {channelOwner.id} WHERE owner_id = {member.id}")
            logger.log(f"User {member.name}({member.id}) left their custom channel in {guild.name}({guild.id}) and set {channelOwner.name}({channelOwner.id}) as the new owner", log_helper.LogTypes.INFO)
            return
        
        if after.channel == None:
            return
        
        if after.channel.id in joinChannels:
            logger.log(f"User {member.name}({member.id}) joined a join channel in {guild.name}({guild.id})", log_helper.LogTypes.INFO)
            joinChannel = joinChannels[joinChannels.index(after.channel.id)]
            joinChannel = guild.get_channel(joinChannel)
            channelOwner = database.execute_read_query(f"SELECT * FROM join_channels WHERE channel_id = {joinChannel.id}")[0][0]
            channelOwner = guild.get_member(channelOwner)
            requestedChannel = database.execute_read_query(f"SELECT * FROM custom_channels WHERE owner_id = {channelOwner.id} AND guild_id = {guild.id}")
            requestedChannel = guild.get_channel(requestedChannel[0][1])
            whitelist = database.execute_read_query(f"SELECT * FROM whitelist WHERE guild_id = {guild.id} AND user_id = {channelOwner.id} AND whitelisted_user_id = {member.id}")
            if whitelist:
                await member.move_to(requestedChannel)
                await joinChannel.set_permissions(member, connect=True)
                logger.log(f"User {member.name}({member.id}) joined {channelOwner.name}({channelOwner.id})'s channel in {guild.name}({guild.id})", log_helper.LogTypes.INFO)
                return
            embed = discord.Embed(title=translation.get_translation(channelOwner.id, "join_channel_request_title"), description=translation.get_translation(channelOwner.id, "join_channel_request", user=member.mention), color=discord.Color.purple())
            embed.set_footer(text="Made with ❤ by the AutoVox team")
            # Add the accept and deny buttons
            class View(discord.ui.View):
                def __init__(self):
                    super().__init__()
                    self.owner = channelOwner
                    self.channel = after.channel
                    self.requestedChannel = requestedChannel
                    self.timeout = 300
                
                async def on_timeout(self):
                    logger.log(f"User {member.name}({member.id}) did not respond to the join channel request from {channelOwner.name}({channelOwner.id}) in {guild.name}({guild.id})", log_helper.LogTypes.INFO)
                    self.disable_all_items()
                    await self.message.edit(view=self)
                    if guild.get_member(member.id).voice.channel == self.channel:
                        await member.move_to(None)
                    

                @discord.ui.button(label=translation.get_translation(channelOwner.id, "accept"), style=discord.ButtonStyle.green)
                async def accept(self, button, interaction):
                    if interaction.user.id != self.owner.id:
                        return
                    user = await interaction.user.guild.fetch_member(member.id)
                    voiceChannel = user.voice.channel
                    if voiceChannel == self.channel:
                        await member.move_to(self.requestedChannel)
                        await requestedChannel.set_permissions(member, connect=True)
                    else:
                        return
                    # Edit the embed to show that the request was accepted
                    embed.color = discord.Color.green()
                    embed.title = translation.get_translation(self.owner.id, "join_channel_request_accepted_title")
                    embed.description = translation.get_translation(self.owner.id, "join_channel_request_accepted", user=member.mention)
                    for child in self.children:
                        child.disabled = True
                    await interaction.edit_original_response(embed=embed, view=self)
                    logger.log(f"User {member.name}({member.id}) joined {self.owner.name}({self.owner.id})'s channel in {guild.name}({guild.id})", log_helper.LogTypes.INFO)

                @discord.ui.button(label=translation.get_translation(channelOwner.id, "deny"), style=discord.ButtonStyle.red)
                async def deny(self, button, interaction):
                    if interaction.user.id != self.owner.id:
                        return
                    if guild.get_member(member.id).voice.channel == after.channel:
                        await member.move_to(None)
                    else:
                        return
                    # Edit the embed to show that the request was denied
                    embed.color = discord.Color.red()
                    embed.title = translation.get_translation(self.owner.id, "join_channel_request_denied_title")
                    embed.description = translation.get_translation(self.owner.id, "join_channel_request_denied", user=member.mention)
                    for child in self.children:
                        child.disabled = True
                    await interaction.edit_original_response(embed=embed, view=self)
                    logger.log(f"User {member.name}({member.id}) denied to join {self.owner.name}({self.owner.id})'s channel in {guild.name}({guild.id})", log_helper.LogTypes.INFO)

            await requestChannel.send(channelOwner.mention,embed=embed, view=View())

            



def setup(bot):
    bot.add_cog(AutoVoice(bot))