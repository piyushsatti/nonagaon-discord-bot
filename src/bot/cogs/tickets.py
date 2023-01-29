import discord
from asyncio import sleep
from discord.ext import commands, tasks

# Code Imports
from classes.colors import bcolors
from classes.base import Base

class Tickets(Base, name="Tickets"):
    """Lets you create tickets"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setTicket(self, ctx, channel: discord.TextChannel):
        '''Sets up tickets'''

        embed = discord.Embed(
            color = self.bot.color,
            title = "Input the title and the description of the ticket (Title | Description)"
            )
        await ctx.send(embed=embed) 
     

        def check(m: discord.Message):
            return m.author == ctx.author

        msg = await self.bot.wait_for('message', timeout=60.0)
        title, desc = msg.content.split("|")
        
        embed = discord.Embed(
            color = self.bot.color,
            title = "Please input the name of the category you'd like new tickets to be in"
            )
        await ctx.send(embed=embed)
        
        category = await self.bot.wait_for('message', timeout=60.0)
        category_id = discord.utils.get(ctx.guild.categories, name=category.content).id
        embed=discord.Embed(
                        title=title.replace(" ", ""), 
                        description=desc.replace(" ", ""),
                        color=self.bot.color
                        )

        msg = await channel.send(embed=embed)
        await msg.add_reaction("📧")

        dbq = '''
        INSERT INTO tickets 
        (guild_id, message_id, category_id)
        VALUES (?,?,?)
        '''

        await self.bot.db.execute(dbq, (str(ctx.guild.id), str(msg.id), str(category_id)))
        await self.bot.db.commit()
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot: 
            return

        if str(payload.emoji) == "📧":

            guild = self.bot.get_guild(payload.guild_id)

            dbq = '''
            SELECT message_id, category_id from tickets
            WHERE guild_id = (?)
            '''
            
            cur = await self.bot.db.execute(dbq, (str(payload.guild_id),))
            res = await cur.fetchone()
            message_id = res[0]
            category_id = int(res[1])

            if str(payload.message_id) == message_id and str(payload.emoji) == "📧":
                category = discord.utils.get(guild.categories, id=category_id)

                overwrites = {
                    payload.member.guild.default_role: discord.PermissionOverwrite(
                        read_messages=False,
                        send_messages=False,
                    ),
                    payload.member: discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                    )
                }

                channel = await category.create_text_channel(name=f'ticket-{payload.user_id}', overwrites=overwrites)
                main_msg = await channel.send(embed=discord.Embed(title="Your ticket", description='React with 🔐 to close.'))
                await main_msg.add_reaction("🔐")

                dbq = '''
                UPDATE tickets
                SET ticket_created_message_id = (?)
                WHERE guild_id = (?) and message_id = (?)
                '''

                await self.bot.db.execute(dbq, (str(main_msg.id), str(guild.id), str(message_id),))
                await self.bot.db.commit()

        if str(payload.emoji) == "🔐":

            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)


            if member.bot: 
                return

            dbq = '''
            SELECT ticket_created_message_id from tickets
            WHERE guild_id = (?)
            '''
            
            cur = await self.bot.db.execute(dbq, (str(payload.guild_id),))
            res = await cur.fetchone()

            ticket_created_message_id = res[0]

            if str(payload.message_id) == ticket_created_message_id:
                channel = discord.utils.get(guild.channels, id=payload.channel_id)

                
                embed=discord.Embed(
                        title="Deleting channel in 5 seconds...", 
                        color=self.bot.color
                )
                await channel.send(embed=embed)
                await sleep(5)
                await channel.delete()

async def setup(bot):
    try: 
        ticket_q = '''
            CREATE TABLE IF NOT EXISTS tickets (
            guild_id VARCHAR,
            message_id VARCHAR,
            category_id VARCHAR,
            ticket_created_message_id VARCHAR DEFAULT '1', 
            PRIMARY KEY (guild_id, message_id))
            '''
        await bot.db.execute(ticket_q)
    except Exception as e:
        print('Error in creating table: timed\n', e)

    await bot.add_cog(Tickets(bot))