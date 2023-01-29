import discord, re
from discord.ext import commands
import emoji, typing

# Code Imports
from classes.colors import bcolors
from classes.base import Base

class Reaction(Base, name="Reaction Roles"):
    """Enables you to create your own reaction roles"""
    def __init__(self, bot):
        self.bot = bot
        self.msg = []
        self.reaction_to_role = {}

    @commands.command()
    async def setroles(self, ctx):
        '''Sets up reaction roles'''

        if await self.command_disabled(ctx.command.cog_name, message.guild.id) != True:

            embed = discord.Embed(
                color = self.bot.color,
                title = "What would you like the message to be?"
                ) 
            await ctx.send(embed=embed)
            
            try:
                main_msg = await self.bot.wait_for('message', timeout=20)
            except TimeoutError:
                await ctx.send("Timed out..")
                return 

            embed = discord.Embed(
                color = self.bot.color,
                title = "What channel would you like the bot to send the reaction message in?"
                )
            await ctx.send(embed=embed)   

            try:
                msg = await self.bot.wait_for('message', timeout=20)
                channel = msg.channel_mentions[0]
                abs_msg = await channel.send(main_msg.content)

                main_msg = await ctx.send("Mention the role please.")
                main_msg_id = main_msg.id

                flag = 0

                while flag == 0:
                    message = await self.bot.wait_for('message', timeout=60.0)
                    if len(message.role_mentions) > 0:
                        if message.content.lower() != 'done':

                            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0)
                            main_msg = await reaction.message.channel.fetch_message(main_msg_id)
                            await main_msg.edit(main_msg.content + '\n' + str(reaction.emoji) + '----' + str(message.role_mentions[0]))

                            self.reaction_to_role[str(reaction.emoji)] = message.role_mentions[0]

                    if message.content.lower() == 'done':
                        
                        flag = 1
                        for emoji in self.reaction_to_role.keys():
                            await abs_msg.add_reaction(emoji)

                            dbq = '''
                            INSERT INTO reaction_roles (message_id, reaction_id, role)
                            VALUES (?, ?, ?)
                            '''
                    
                            try:
                                await self.bot.db.execute(dbq, (str(abs_msg.id), str(emoji), self.reaction_to_role[emoji].id))
                                await self.bot.db.commit()
                            except Exception as e:
                                await ctx.send(str(e))




            except TimeoutError:
                await ctx.send("timed out.. try again")


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot: 
            return

        dbq = '''
        SELECT message_id from reaction_roles
        WHERE reaction_id = (?)
        '''
        
        cur = await self.bot.db.execute(dbq, (str(payload.emoji),))
        message_id = await cur.fetchone()

        if str(payload.message_id) == message_id[0]:

            dbq = '''
            SELECT role from reaction_roles
            WHERE reaction_id = (?) AND message_id = (?)
            '''
            cur = await self.bot.db.execute(dbq, (str(payload.emoji), message_id[0]))
            role = await cur.fetchone()

            guild = self.bot.get_guild(payload.guild_id)
            await payload.member.add_roles(guild.get_role(int(role[0])))

    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if member.bot: 
            return

        dbq = '''
        SELECT message_id from reaction_roles
        WHERE reaction_id = (?)
        '''
        
        cur = await self.bot.db.execute(dbq, (str(payload.emoji),))
        message_id = await cur.fetchone()

        if str(payload.message_id) == message_id[0]:

            dbq = '''
            SELECT role from reaction_roles
            WHERE reaction_id = (?) AND message_id = (?)
            '''
            cur = await self.bot.db.execute(dbq, (str(payload.emoji), message_id[0]))
            role = await cur.fetchone()
            
            await member.remove_roles(guild.get_role(int(role[0])))

async def setup(bot):
    try:
        reaction_q = '''CREATE TABLE IF NOT EXISTS reaction_roles (
            message_id VARCHAR, 
            reaction_id VARCHAR,
            role VARCHAR, 
            PRIMARY KEY (message_id, reaction_id))'''
        await bot.db.execute(reaction_q)
    except Exception as e:
        print('Error in creating table: reaction_roles\n', e)

    await bot.add_cog(Reaction(bot))