import os
from dotenv import load_dotenv, find_dotenv
import discord
from discord.ext import commands

from cogs.private_channels import PrivateChannels
from cogs.check_in import CheckIn

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print("Ready...")

# Si no necesitas la funcionalidad del check in, comenta o elimina
# la siguiente línea.
bot.add_cog(CheckIn(bot))

# Si no necesitas la funcionalidad de los canales privados, comenta o elimina
# la siguiente línea.
bot.add_cog(PrivateChannels(bot))

load_dotenv(find_dotenv())
DISCORD_KEY = os.environ.get("DISCORD")

bot.run(DISCORD_KEY)
