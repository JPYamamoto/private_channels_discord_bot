from tinydb import TinyDB, Query, where

class _Database:
    _instance = None

    def __init__(self):
        self.db = TinyDB('participants.json')
        self.members = self.db.table('members')
        self.teams = self.db.table('teams')

    def register_team(self, members, team, channel_id):
        team_id = self.teams.insert({'channel': channel_id, 'name': team})
        docs = [{'id': member.id, 'team': team_id} for member in members]
        self.members.insert_multiple(docs)

    def team_exists(self, team):
        res = self.get_team_by_name(team)

        if not res:
            return False

        return len(res) != 0

    def get_team_by_name(self, team):
        Team = Query()
        return self.teams.get(Team.name == team)

    def get_team_by_id(self, team):
        return self.teams.get(doc_id=team)

    def remove_team(self, team):
        Team = Query()
        team = self.teams.get(Team.name == team)

        if not team:
            return

        self.teams.remove(doc_ids=[team.doc_id])
        self.members.remove(where('team') == team.doc_id)
        return team['channel']

    def user_team(self, user_discord_id):
        User = Query()
        found_user = self.members.get(User.id == user_discord_id)

        if found_user and found_user['team']:
            return self.get_team_by_id(found_user['team'])

        return None


def Database():
    if _Database._instance is None:
        _Database._instance = _Database()
    return _Database._instance

