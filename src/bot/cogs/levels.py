from logging import exception
import discord, asyncio
from datetime import datetime, timedelta
from random import randint
from discord.ext import commands
from discord import Member
from typing import Optional

# Code Imports
from classes.colors import bcolors
from classes.base import Base

class Levels(Base, name="Levels"):
    """The Levelling/XP system"""
    def __init__(self, bot):
        self.bot = bot

    async def updateInv(self, guild_id, member_id, increment=True):
        update_query = '''
        UPDATE level_system 
        SET invites = invites {} 1 
        WHERE guild_id = (?) AND
        member_id = (?)
        '''.format('+' if increment else '-')
        await self.bot.db.execute(update_query, (str(guild_id), str(member_id),))
        await self.bot.db.commit()

    async def process_xp(self, message):
        cur = await self.bot.db.execute("SELECT exp, exp_lock FROM level_system WHERE guild_id = ? AND member_id = ?", (str(message.guild.id), str(message.author.id)))
        xp, xplock = await cur.fetchone()
        if datetime.utcnow() > datetime.fromisoformat(xplock):
            await self.add_xp(message, xp)

    async def add_xp(self, message, xp):
        lvl = int(((xp)//42) ** 0.55)
        xp_to_add = randint(10, 20)
        new_lvl = int(((xp+xp_to_add)//42) ** 0.55)

        expq = '''
        UPDATE level_system 
        SET exp = exp + (?), exp_lock = (?)
        WHERE guild_id = (?) AND member_id = (?)
        '''
        await self.bot.db.execute(
            expq, 
                (
                xp_to_add, 
                (datetime.utcnow()+timedelta(seconds=1)).isoformat(), 
                str(message.guild.id), 
                str(message.author.id),
                )
            )
        await self.bot.db.commit()

        if new_lvl > lvl:
            embed = discord.Embed(
                color = self.bot.color,
                description = f"***Congrats {message.author.mention} - you reached level {new_lvl}!***"
            )

            await message.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if await self.command_disabled("Levels", message.guild.id) != True:
            if not message.author.bot:
                checkq = '''
                SELECT EXISTS(SELECT 1 FROM level_system WHERE member_id = (?) AND guild_id = (?))
                '''
                cur = await self.bot.db.execute(checkq, (str(message.author.id), str(message.guild.id)))
                res = (await cur.fetchone())[0]
                if res:
                    await self.process_xp(message)
                else:
                    levelq = '''
                        INSERT INTO level_system (guild_id, member_id) 
                        VALUES (?, ?)
                        '''
                    await self.bot.db.execute(levelq, (str(message.guild.id), str(message.author.id),))
                    await self.bot.db.commit()


    @commands.command()
    async def level(self, ctx, target: Optional[Member]):

        '''Shows the user's level'''

        if await self.command_disabled(ctx.command.cog_name, ctx.guild.id) != True:

            target = target or ctx.author

            levelq = '''
            SELECT exp 
            FROM level_system 
            WHERE guild_id = (?) AND member_id = (?)
            '''
            cur = await self.bot.db.execute(levelq, (str(ctx.guild.id), str(ctx.author.id)))
            xp = (await cur.fetchone())[0]
            if xp:

                embed = discord.Embed(
                    color = self.bot.color,
                    title = f"***{target.display_name} is on level {int(((xp)//42) ** 0.55):,} with {xp:,} XP.***"
                )
                await ctx.send(embed=embed)

            else:

                embed = discord.Embed(
                    color = self.bot.color,
                    title = f"***{target.display_name} is not tracked by the experience system.***"
                )
                await ctx.send(embed=embed)


    @commands.command()
    async def leaderboard(self, ctx):
        '''Displays the top 50 members sorted by XP'''
        if await self.command_disabled(ctx.command.cog_name, ctx.guild.id) != True:

            buttons = {}
            for i in range(1, 6): 
                buttons[f"{i}\N{COMBINING ENCLOSING KEYCAP}"] = i 

            previous_page = 0
            current = 1
            index = 1
            entries_per_page = 10

            embed = discord.Embed(title=f"Leaderboard Page {current}", description="", colour=self.bot.color)
            msg = await ctx.send(embed=embed)

            for button in buttons:
                await msg.add_reaction(button)

            while True:
                if current != previous_page:
                    embed.title = f"Leaderboard Page {current}"
                    embed.description = ""

                    cur = await self.bot.db.execute(f"SELECT member_id, exp FROM level_system WHERE guild_id = ? ORDER BY exp DESC LIMIT ? OFFSET ? ", (str(ctx.guild.id), entries_per_page, entries_per_page*(current-1),))
                    index = entries_per_page*(current-1)

                    async for entry in cur:
                        index += 1
                        member_id, exp = entry
                        member = ctx.guild.get_member(int(member_id))
                        embed.description += f"{index}) {member.mention} : {exp}\n"

                    await msg.edit(embed=embed)
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)
                    except asyncio.TimeoutError:
                        return await msg.clear_reactions()
                else:
                    previous_page = current
                    await msg.remove_reaction(reaction.emoji, ctx.author)
                    current = buttons[reaction.emoji]

    @commands.Cog.listener()
    async def on_member_join(self, member):
        inviter = await self.bot.tracker.fetch_inviter(member)
        await self.updateInv(member.guild.id, inviter.id, True)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        inviter = await self.bot.tracker.fetch_inviter(member)
        await self.updateInv(member.guild.id, inviter.id, False)

async def setup(bot):
    try:
        levelq = '''CREATE TABLE IF NOT EXISTS level_system (
            guild_id VARCHAR, 
            member_id VARCHAR, 
            exp int DEFAULT 0, 
            invites int DEFAULT 0,
            exp_lock text DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (guild_id, member_id))'''
        await bot.db.execute(levelq)
    except Exception as e:
        print('Error in creating table: level_system\n', e)

    await bot.add_cog(Levels(bot))

"""
    @commands.command()
    async def leaderboard(self, ctx):

        lbq = '''
        SELECT member_id, exp 
        FROM level_system 
        WHERE guild_id = (?)
        ORDER BY exp DESC
        '''

        try:
            cur = await self.bot.db.execute(lbq, (str(ctx.guild.id),))
            res_ = await cur.fetchall()


        except Exception as e:
            print('Error in leaderboard:\n', e)

        res = [list(ele) for ele in res_]
"""