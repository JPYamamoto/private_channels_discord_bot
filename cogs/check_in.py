import discord
import typing
import csv
from discord.ext import commands

ARCHIVO_CSV = 'participantes.csv'
COLUMNA_CSV = 6
NOMBRE_CANAL = 'check-in'
AGREGAR_ROLES = ['noauth']
ELIMINAR_ROLES = ['no-check']
REDIRIGIR_CANAL = 'codigo-de-conducta'

class CheckIn(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.emails_registrados = set()

        with open(ARCHIVO_CSV, encoding='utf-8') as f:
            reader = csv.reader(f)
            reader.__next__()
            self.emails_mentores = set(user[COLUMNA_CSV].lower().strip() for user in reader)


    @commands.command()
    async def check(self, ctx, email: str):
        if ctx.channel.name != NOMBRE_CANAL:
            return

        await ctx.message.delete()
        email = email.strip()

        if email == '':
            await ctx.send(f"No ingresaste un correo válido, {ctx.author.mention}")
            return

        if email.lower() in self.emails_registrados:
            roles = [discord.utils.get(ctx.guild.roles, name=r) for r in AGREGAR_ROLES]
            roles_del = [discord.utils.get(ctx.guild.roles, name=r) for r in ELIMINAR_ROLES]

            for role in roles:
                await ctx.message.author.add_roles(role)

            for role in roles_del:
                await ctx.message.author.remove_roles(roles_del)

            channel = discord.utils.get(ctx.guild.channels, name=REDIRIGIR_CANAL)
            await ctx.send(f"Bienvenid@ {ctx.message.author.mention}! Por favor, dirígete al canal {channel.mention}.")
        else:
            await ctx.send(f"{ctx.author.mention}, no tenemos registrado el email que ingresaste.")

