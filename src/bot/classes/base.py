import json
from discord.ext import commands

class Base(commands.Cog, name="base"):
    def __init__(self, bot):
        self.bot = bot

    async def test(self):
        try:
            print(40)
        except Exception as e:
            print(e)

    async def command_disabled(self, cog_name, guild_id):
        try:
            if cog_name.lower() in self.bot.disabled[str(guild_id)]['commands']:
                return True
            else:
                return False
        except Exception as e:
            print(e)

    async def fetchDisabled(self):
        fetch_cmd_status = '''
        SELECT disabled 
        FROM guild_data
        WHERE guild_id = (?)
        '''

        for guild in self.bot.guilds:
            cur =  await self.bot.db.execute(fetch_cmd_status, (str(guild.id),))
            res = await cur.fetchone()
            jso = json.loads(res[0])

            self.bot.disabled[str(guild.id)] = jso


        for guild in self.bot.guilds:
            for cog in self.bot.cogs:
                if not self.bot.disabled[str(guild.id)][cog]:
                    self.bot.disabled[str(guild.id)][cog] = 'True'

        print(self.bot.disabled)