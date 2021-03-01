import discord
import typing
import csv
from discord.ext import commands


class PrivateChannels(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.emails_registrados = set()
        self.emails_mentores = set()

        with open('data_mentores.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            reader.__next__()
            self.emails_mentores = set(user[6].lower().strip() for user in reader)

        with open('data.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            reader.__next__()
            self.emails_registrados = set(user[10].lower().strip() for user in reader)


    @commands.command()
    async def team(self, ctx, name: str, members: commands.Greedy[discord.Member]):
        if ctx.channel.name != "crear-equipo":
            return

        members = list(set(members))

        try:
            if len(members) < 3 or len(members) > 5 :
                raise ValueError("Los equipos deben tener entre 3 y 5 integrantes.")

            channel = await self.create_team_channel(ctx.guild, members, name)
            await self.create_team_voice(ctx.guild, members, channel.name)

            await ctx.send(f"Bienvenidos equipo \"{name}\"!\n"
                            "Ya pueden acceder a su canal privado.", reference=ctx.message)
        except ValueError:
            message = f"{ctx.author.mention} hubo un error al registrar a tu equipo \"{name}\"."
            await ctx.send(message, reference=ctx.message)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unteam(self, ctx, team_channel: typing.Union[discord.TextChannel, discord.VoiceChannel]):
        if ctx.channel.name != "crear-equipo" and ctx.channel.name != team_channel.name:
            return

        name = team_channel.name
        channel = discord.utils.get(ctx.guild.channels, name=name)
        voice = discord.utils.get(ctx.guild.voice_channels, name=name)

        await channel.delete()
        await voice.delete()
        await ctx.send(f"Se ha eliminado el equipo \"{name}\".", reference=ctx.message)


    @unteam.error
    async def unteam_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"{ctx.author.mention} No tienes permisos para eliminar equipos.",
                           reference=ctx.message)
        else:
            raise error


    @commands.command()
    async def kick(self, ctx, team: typing.Union[discord.TextChannel, discord.VoiceChannel], member: discord.Member):
        if ctx.channel.name != "crear-equipo" and ctx.channel.name != team.name:
            return

        try:
            is_admin = ctx.message.author.guild_permissions.administrator
            if not is_admin and not (ctx.message.author not in team.members):
                await ctx.send(f"{ctx.author.mention} No tienes permisos para sacar a {member.mention} del equipo"
                                 "{team.name}.", reference=ctx.message)
                return

            if member not in team.members:
                await ctx.send(f"Error. El usuario {member.mention} no es parte del equipo {team}.",
                               reference=ctx.message)
            else:
                name = team.name
                channel = discord.utils.get(ctx.guild.channels, name=name)
                voice = discord.utils.get(ctx.guild.voice_channels, name=name)

                await channel.set_permissions(member, read_messages=False, send_messages=False)
                await voice.set_permissions(member, read_messages=False, send_messages=False)

                await ctx.send(f"Se ha eliminado a {member} del equipo {team}.", reference=ctx.message)
        except ValueError:
            message = f"{ctx.author.mention} hubo un error al eliminar a {member.mention} del equipo \"{team}\"."
            await ctx.send(message, reference=ctx.message)


    @commands.command()
    async def check(self, ctx, email: str):
        if ctx.channel.name != "check-in":
            return

        await ctx.message.delete()
        email = email.strip()

        if email == '':
            await ctx.send(f"No ingresaste un correo válido, {ctx.author.mention}")
            return

        if email.lower() in self.emails_mentores:
            role1 = discord.utils.get(ctx.guild.roles, name= 'mentor')
            role_del = discord.utils.get(ctx.guild.roles, name= 'no-check')
            await ctx.message.author.add_roles(role1)
            await ctx.message.author.remove_roles(role_del)
            channel = discord.utils.get(ctx.guild.channels, name='codigo-de-conducta')
            await ctx.send(f"Bienvenido {ctx.message.author.mention}! Por favor, dirígete al canal {channel.mention}.")
        elif email.lower() in self.emails_registrados:
            role = discord.utils.get(ctx.guild.roles, name= 'noauth')
            role_del = discord.utils.get(ctx.guild.roles, name= 'no-check')
            await ctx.message.author.add_roles(role)
            await ctx.message.author.remove_roles(role_del)
            channel = discord.utils.get(ctx.guild.channels, name='codigo-de-conducta')
            await ctx.send(f"Bienvenido {ctx.message.author.mention}! Por favor, dirígete al canal {channel.mention}.")
        else:
            await ctx.send(f"{ctx.author.mention}, no tenemos un usuario registrado con el email que ingresaste.")


    async def create_team_channel(self, guild, members, team):
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        for member in members:
            overwrites[member] = discord.PermissionOverwrite(read_messages=True, create_instant_invite=False)

        category = next(c for c in guild.categories if c.name.lower() == 'equipos2')

        channel = await guild.create_text_channel(team, overwrites=overwrites, category=category,
                                                  topic=f"Canal privado para el equipo {team}")

        return channel

    async def create_team_voice(self, guild, members, team):
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        for member in members:
            overwrites[member] = discord.PermissionOverwrite(read_messages=True, create_instant_invite=False)

        category = next(c for c in guild.categories if c.name.lower() == 'equipos2')

        channel = await guild.create_voice_channel(team, overwrites=overwrites, category=category,
                                                   topic=f"Canal de voz privado para el equipo {team}")

        return channel

