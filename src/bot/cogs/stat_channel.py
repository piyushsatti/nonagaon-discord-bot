import discord
from discord.ext import commands, tasks

# Code Imports
from classes.colors import bcolors
from classes.base import Base

class Stats(Base, name="Stats"):
    """Creates a channel to show server information"""
    def __init__(self, bot):
        self.bot = bot
        self.stat_fetch.start()

    @commands.command()
    async def setStats(self, ctx):

        category = await ctx.guild.create_category("Server Info")
        channel = await category.create_voice_channel(f"Members: {len(ctx.guild.members)}")

        ov = discord.PermissionOverwrite()
        ov.connect = False

        await channel.set_permissions(
                overwrite=ov,
                target=ctx.guild.default_role
            )

        dbq = '''
        INSERT INTO stat_channel 
        (guild_id, channel_id)
        VALUES (?,?)
        '''

        await self.bot.db.execute(dbq, (str(ctx.guild.id), str(channel.id),))
        await self.bot.db.commit()
        await ctx.send("Created a stat channel for this server! The counter will be updated every 10 minutes!")

    @tasks.loop(seconds=600)
    async def stat_fetch(self):

        stat_q = '''
        SELECT channel_id
        FROM stat_channel
        '''

        cur = await self.bot.db.execute(stat_q)
        res = await cur.fetchall()

        try:
            for channel in res:
                vc = self.bot.get_channel(int(channel[0]))
                await vc.edit(name=f'Members: {len(vc.guild.members)}')

        except Exception as e:
            pass

    @stat_fetch.before_loop
    async def before_stat_fetch(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    try:
        reaction_q = '''CREATE TABLE IF NOT EXISTS stat_channel (
            guild_id VARCHAR, 
            channel_id VARCHAR,
            PRIMARY KEY (guild_id))'''
        await bot.db.execute(reaction_q)
    except Exception as e:
        print('Error in creating table: Stats\n', e)

    await bot.add_cog(Stats(bot))