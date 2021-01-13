import discord
from discord.ext import commands
from tinydb import TinyDB, Query, where


class PrivateChannels(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.db = TinyDB('participants.json')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unteam(self, ctx, team_name):
        if self.team_exists(team_name):
            self.remove_team(team_name)
            await ctx.send(f"Se ha eliminado el equipo \"{team_name}\".\n",
                           reference=ctx.message)
        else:
            await ctx.send(f"No existe el equipo \"{team_name}\".\n", reference=ctx.message)

    @unteam.error
    async def unteam_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"{ctx.author.mention} No tienes permisos para eliminar equipos.",
                           reference=ctx.message)
        else:
            raise error

    @commands.command()
    async def team(self, ctx, name: str, members: commands.Greedy[discord.Member]):
        members.append(ctx.author)
        members = list(set(members))

        try:
            self.validate(members)
            self.register_team(members, name)
            await self.create_team_channel(ctx.guild, members, name)
            await ctx.send(f"Bienvenidos equipo \"{name}\"!\n"
                            "Ya pueden acceder a su canal privado.", reference=ctx.message)
        except ValueError as ve:
            message = f"{ctx.author.mention} hubo un error al registrar a tu equipo \"{name}\".\n{ve}"
            await ctx.send(message, reference=ctx.message)


    def validate(self, members):
        if len(members) < 3 or len(members) > 5 :
            raise ValueError("Los equipos deben tener entre 3 y 5 integrantes.")

        u_teams = [u for u in members if self.user_team(u.id)]

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

        await guild.create_text_channel(team, overwrites=overwrites, category=category,
                                        topic=f"Canal privado para el equipo {team}")

    def user_team(self, user_id):
        User = Query()
        found_user = self.db.search(User.id == user_id)

        if found_user and found_user[0]['team']:
            return found_user[0]['team']

        return None

    def register_team(self, members, team):
        self.db.insert_multiple([{'id': member.id, 'team': team} for member in members])

    def team_exists(self, team):
        User = Query()
        return len(self.db.search(User.team == team)) != 0

    def remove_team(self, team):
        self.db.remove(where('team') == team)

