import os
from dotenv import load_dotenv, find_dotenv
import discord
from discord.ext import commands

from cogs.private_channels import PrivateChannels

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print("Ready...")

bot.add_cog(PrivateChannels(bot))

load_dotenv(find_dotenv())
DISCORD_KEY = os.environ.get("DISCORD")

bot.run(DISCORD_KEY)
