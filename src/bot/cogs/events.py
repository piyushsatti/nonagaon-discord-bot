import discord, sys
from discord.ext import commands
from requests import PreparedRequest

# Code Imports
from classes.colors import bcolors
from classes.base import Base

class Events(Base):

    def __init__(self, bot):
        self.bot = bot

    async def addGuildsToDB(self, data):
        query = '''
            INSERT INTO guild_data (guild_id) VALUES (?)
            '''
        for ele in data:
            await self.bot.db.execute(query, (ele,))
        await self.bot.db.commit()

        print('adding guilds...',data)
    
    async def leaveGuildsFromDB(self, data):
        query = '''
            DELETE FROM guild_data
            WHERE guild_id = (?)
            '''
        for ele in data:
            await self.bot.db.execute(query, (ele,))
        await self.bot.db.commit()

        print('removing guilds...', data)

    async def checkGuilds(self):
        '''
        DB_GUILD - BOT_GUILDS = KICK
        BOT_GUILDS - DB_GUILD = ADD
        '''
        bot_guilds = [guild.id for guild in self.bot.guilds]
        guild_fetch_query = '''
        SELECT guild_id
        FROM guild_data
        '''
        cur = await self.bot.db.execute(guild_fetch_query)
        res = await cur.fetchall()
        db_guilds = [int(ele[0]) for ele in res]
        if list(db_guilds) != bot_guilds:
            add_ = list(set(bot_guilds) - set(db_guilds))
            remove_ = list(set(db_guilds) - set(bot_guilds))
            print(add_, 'llll', remove_)
            if len(add_) != 0: await self.addGuildsToDB(add_)
            if len(remove_) != 0: await self.leaveGuildsFromDB(remove_)


    @commands.Cog.listener()
    async def on_ready(self):
        await self.checkGuilds()
        print('Ready!')
        print('Logged in as ---->', self.bot.user)
        print('ID:', self.bot.user.id)


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            q = '''
            SELECT command_name FROM custom_commands
            WHERE guild_id = (?)
            '''
            cur = await self.bot.db.execute(q, (ctx.guild.id,))
            res_ = await cur.fetchall()
            res = [ele[0] for ele in res_]
            if ctx.message.content.split(' ', 1)[0][1:] not in res:
                await ctx.send("**Invalid command. Try** `help` **to figure out commands**")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('**Please pass in all requirements.**')
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("**You dont have all the requirements or permissions for using this command :angry:**")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            await self.bot.db.execute("INSERT INTO guild_data (guild_id) VALUES (?)", (str(guild.id),))
            await self.bot.db.commit()
            print(f"Guild <{guild.id}> added to DB.")
        except Exception as e:
            print(f"Exception on Guild_Join for guild {guild.id}:\n", e)

    
    
    @commands.Cog.listener()
    async def on_member_join(self, member):

        
        embed = discord.Embed(colour=discord.Colour.green())
        fetch_welc_id = '''
                SELECT welcome_channel_id 
                FROM guild_data
                WHERE guild_id = (?)
        '''
        cur = await self.bot.db.execute(fetch_welc_id, (str(member.guild.id),))
        res = await cur.fetchone()
        channel = self.bot.get_channel(int(res[0]))
        req = PreparedRequest()
        req.prepare_url(
            url='https://api.xzusfin.repl.co/card?',
            params={
                'avatar': str(member.display_avatar.url),
                'middle': 'welcome',
                'name': str(member.name),
                'bottom': str('on ' + member.guild.name),
                'text': '#CCCCCC',
                'avatarborder': '#CCCCCC',
                'avatarbackground': '#CCCCCC',
                'background': '#000000' #or image url
            }
        )
        embed.set_image(url=req.url)
        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Events(bot))
