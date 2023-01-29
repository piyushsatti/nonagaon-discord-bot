import discord
from discord.ext import commands, tasks

# Code Imports
from classes.colors import bcolors
from classes.base import Base

class Timed(Base, name="Timed Messages"):
    """Makes the bot send messages periodically"""
    def __init__(self, bot):
        self.bot = bot
        self.printer.start()
        self.time_interval = 0

    @commands.command(name="create_timed_msg")
    async def create_timed_message(self, ctx, channel: discord.TextChannel, period, *args):
        '''Creates new timed message'''
        if await self.command_disabled(ctx.command.cog_name, ctx.guild.id) != True:
            msg = ' '.join(args)

            try:
                dbq = '''
                    INSERT OR REPLACE INTO timed_msgs
                    (guild_id, channel_id, period, message)
                    VALUES (?,?,?,?)
                '''
                await self.bot.db.execute(dbq, (ctx.guild.id, channel.id, period, msg))
                await self.bot.db.commit()
            except Exception as e:
                print("Exception in create_timed_message:\n", e)
            embed = discord.Embed(
                color = self.bot.color,
                title = f"Timed message `{msg}` now periodic every `{period}` min"
                )
            await ctx.send(embed=embed)   

    

    @commands.command()
    async def deletetimedmessage(self, ctx, channel: discord.TextChannel, period, message):
        '''Deletes timed message'''
        if await self.command_disabled(ctx.command.cog_name, ctx.guild.id) != True:
            try:
                q = '''
                DELETE FROM timed_msgs
                WHERE guild_id = (?) AND channel_id = (?) AND period = (?) AND message = (?)
                '''
                await self.bot.db.execute(q, (str(ctx.guild.id), str(channel.id), period, message))
                await self.bot.db.commit()

                await ctx.send(embed=discord.Embed(title=f"Deleted timed message `{message}` in {channel.name}.", color=self.bot.color))

            except Exception as e:
                print('Exception in deletetimedmessage:\n',e)
        
  
    @commands.command()
    async def listtimedmessages(self, ctx):
        '''Displays all the timed messages in the guild'''
        if await self.command_disabled(ctx.command.cog_name, ctx.guild.id) != True:
            try:
                q = '''
                SELECT channel_id, period, message FROM timed_msgs
                WHERE guild_id = (?)
                '''
                res_ = await (await self.bot.db.execute(q,(ctx.guild.id,))).fetchall()
                embed = discord.Embed(
                color = self.bot.color,
                title = f"All timed messages for {ctx.guild.name}\n"
                )
                
                for res in res_:
                    embed.add_field(name=res[2], value=f"{res[1]} minutes in {self.bot.get_channel(int(res[0])).mention}", inline=False)

                await ctx.send(embed=embed)
            except Exception as e:
                print('Exception in listtimedmessages:\n',e)

    @tasks.loop(seconds=60.0)
    async def printer(self):
        self.time_interval += 1
        dbq = '''
        SELECT * from timed_msgs
        '''
        cur = await self.bot.db.execute(dbq)
        res_ = await cur.fetchall()
        for res in res_:
            if self.time_interval % int(res[2]) == 0:
                channel = self.bot.get_channel(int(res[1]))
                await channel.send(res[3])

    @printer.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    try:
        timed_q = '''
            CREATE TABLE IF NOT EXISTS timed_msgs (
            guild_id VARCHAR, 
            channel_id VARCHAR, 
            period VARCHAR,
            message VARCHAR)
            '''
        await bot.db.execute(timed_q)
    except Exception as e:
        print('Error in creating table: timed\n', e)

    await bot.add_cog(Timed(bot))