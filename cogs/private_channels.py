import discord
from discord.ext import commands
from tinydb import TinyDB, Query, where
from .database import Database


class PrivateChannels(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.db = Database()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unteam(self, ctx, team_name):
        if self.db.team_exists(team_name):
            channel_id, voice_id = self.db.remove_team(team_name)
            channel = self.client.get_channel(channel_id)
            voice = self.client.get_channel(voice_id)
            await channel.delete()
            await voice.delete()
            await ctx.send(f"Se ha eliminado el equipo \"{team_name}\".\n",
                           reference=ctx.message)
        else:
            await ctx.send(f"No existe el equipo \"{team_name}\".\n", reference=ctx.message)

    @commands.command()
    async def team(self, ctx, name: str, members: commands.Greedy[discord.Member]):
        members = list(set(members))

        try:
            self.validate(members)
            channel_id = await self.create_team_channel(ctx.guild, members, name)
            voice_id = await self.create_team_voice(ctx.guild, members, name)
            self.db.register_team(members, name, channel_id, voice_id)
            await ctx.send(f"Bienvenidos equipo \"{name}\"!\n"
                            "Ya pueden acceder a su canal privado.", reference=ctx.message)
        except ValueError:
            message = f"{ctx.author.mention} hubo un error al registrar a tu equipo \"{name}\"."
            await ctx.send(message, reference=ctx.message)

    @commands.command()
    async def kick(self, ctx, team: str, member: discord.Member):
        try:
            author_team = self.db.user_team(ctx.message.author.id)
            is_admin = ctx.message.author.guild_permissions.administrator
            if not is_admin and not (author_team and author_team['name'] == team):
                await ctx.send(f"{ctx.author.mention} No tienes permisos para sacar a {member.mention} del equipo {team}.",
                               reference=ctx.message)
                return

            member_team = self.db.user_team(member.id)
            if not member_team or member_team['name'] != team:
                await ctx.send(f"Error. El usuario {member.mention} no es parte del equipo {team}.",
                               reference=ctx.message)
            else:
                channel_id, voice_id = member_team['channel'], member_team['voice']
                channel = self.client.get_channel(channel_id)
                voice = self.client.get_channel(voice_id)

                await channel.set_permissions(member, read_messages=False, send_messages=False)
                await voice.set_permissions(member, read_messages=False, send_messages=False)
                self.db.remove_user(member.id)

                await ctx.send(f"Se ha eliminado a {member} del equipo {team}.", reference=ctx.message)
        except ValueError:
            message = f"{ctx.author.mention} hubo un error al eliminar a {member.mention} del equipo \"{team}\"."
            await ctx.send(message, reference=ctx.message)


    @unteam.error
    async def unteam_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"{ctx.author.mention} No tienes permisos para eliminar equipos.",
                           reference=ctx.message)
        else:
            raise error

    def validate(self, members):
        if len(members) < 3 or len(members) > 5 :
            raise ValueError("Los equipos deben tener entre 3 y 5 integrantes.")

        u_teams = [u for u in members if self.db.user_team(u.id)]

        if u_teams:
            message = ""

            for member in u_teams:
                message += f"- {member.mention} se encuentra registrado en un equipo distinto.\n"

            raise ValueError(message)

    async def create_team_channel(self, guild, members, team):
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        for member in members:
            overwrites[member] = discord.PermissionOverwrite(read_messages=True, create_instant_invite=False)

        category = next(c for c in guild.categories if c.name == 'Teams')

        channel = await guild.create_text_channel(team, overwrites=overwrites, category=category,
                                                  topic=f"Canal privado para el equipo {team}")

        return channel.id

    async def create_team_voice(self, guild, members, team):
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        for member in members:
            overwrites[member] = discord.PermissionOverwrite(read_messages=True, create_instant_invite=False)

        category = next(c for c in guild.categories if c.name == 'Teams')

        channel = await guild.create_voice_channel(team, overwrites=overwrites, category=category,
                                                   topic=f"Canal de voz privado para el equipo {team}")

        return channel.id

