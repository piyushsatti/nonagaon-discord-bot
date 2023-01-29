import discord, asyncio, sys, json
from discord.ext import commands

# Code Imports
from classes.colors import bcolors
from classes.base import Base

class Mod(Base, name="Moderation"):
    """Commands for server moderators"""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, prefix):
        '''Sets the bot's prefix for the guild.'''

        try:
            set_prefix_q = '''
            UPDATE guild_data 
            SET guild_prefix = (?) 
            WHERE guild_id = (?)
            '''
            await self.bot.db.execute(set_prefix_q, (prefix, str(ctx.guild.id),))
            await self.bot.db.commit()
            await ctx.send(f"Prefix changed: {prefix}")
        except Exception as e:
            print("Exception in set_prefix:\n", e)

    @commands.command()
    @commands.has_permissions(kick_members=True)

    async def kick(self, ctx, member : discord.Member, *, reason=None):
        '''Kicks the user'''
        await member.kick(reason=reason)
        embed = discord.Embed(
            color = self.bot.color,
            title = f"***{member.name} has been kicked.***"
        )
        await ctx.send(embed=embed)
        
    
    @commands.command()
    @commands.has_permissions(ban_members=True) 

    async def ban(self, ctx, member : discord.Member, *, reason=None):
        '''Bans the user'''
        await member.ban(reason=reason)
        embed = discord.Embed(
            color = self.bot.color,
            title = f"***{member.name} has been banned.***"
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True) 

    async def unban(self, ctx, user_id : int):
        '''Unbans the user'''
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        embed = discord.Embed(
            color = self.bot.color,
            title = f"***{user.name} has been banned.***"
        )
        await ctx.send(embed=embed)


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, member : discord.Member, days, reason=None):
        '''Bans the user for the given number of days'''

        days * 5 

        await member.ban(reason=reason)
        embed = discord.Embed(
            color = self.bot.color,
            title = f"***{member.name} has been soft-banned for {days} days.***"
        )
        await ctx.send(embed=embed)

        await asyncio.sleep(days)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setWelcome(self, ctx, channel: discord.TextChannel):
        update_welc_status = '''
            UPDATE guild_data 
            SET welcome_channel_id = (?) 
            WHERE guild_id = (?)
            '''

        await self.bot.db.execute(update_welc_status, (str(channel.id), str(ctx.guild.id),))
        await ctx.send(f"Updated welcome channel to {channel.mention}!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx, *, command):

        if command.lower() in [key.lower() for key in self.bot.cogs.keys()]:
            try:
                fetch_cmd_status = '''
                SELECT disabled 
                FROM guild_data
                WHERE guild_id = (?)
                '''
                cur =  await self.bot.db.execute(fetch_cmd_status, (str(ctx.guild.id),))
                res = await cur.fetchone()
                jso = json.loads(res[0])

                try:

                    if command.lower() not in [cmd.lower() for cmd in jso['commands']]:
                        jso['commands'].append(command.lower())

                        update_cmd_status = '''
                        UPDATE guild_data 
                        SET disabled = (?) 
                        WHERE guild_id = (?)
                        '''
    
                        await self.bot.db.execute(update_cmd_status, (json.dumps(jso), str(ctx.guild.id),))
                        await self.fetchDisabled()
                        await ctx.send(jso)

                    else:

                        await ctx.send(f"The command `{command}` is already disabled")

                except:

                    jso['commands'] = []
                    jso['commands'].append(command.lower())

                    update_cmd_status = '''
                    UPDATE guild_data 
                    SET disabled = (?) 
                    WHERE guild_id = (?)
                    '''
                    await self.bot.db.execute(update_cmd_status, (json.dumps(jso), str(ctx.guild.id),))
                    await self.fetchDisabled()
                    await ctx.send(jso)

            except Exception as e:
                print("Exception in disable:\n", e)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx, *, command):

        if command.lower() in [key.lower() for key in self.bot.cogs.keys()]:
            try:
                fetch_cmd_status = '''
                SELECT disabled 
                FROM guild_data
                WHERE guild_id = (?)
                '''
                cur =  await self.bot.db.execute(fetch_cmd_status, (str(ctx.guild.id),))
                res = await cur.fetchone()
                jso = json.loads(res[0])
       
                try:

                    if command.lower() in [cmd.lower() for cmd in jso['commands']]:
                        jso['commands'].remove(command.lower())
                        update_cmd_status = '''
                        UPDATE guild_data 
                        SET disabled = (?) 
                        WHERE guild_id = (?)
                        '''

                        await self.bot.db.execute(update_cmd_status, (json.dumps(jso), str(ctx.guild.id),))
                        await self.fetchDisabled()
                        await ctx.send(jso)
    

                    else:
                        await ctx.send(f"The command `{command}` is already enabled!")

                except:

                    jso['commands'] = []

                    update_cmd_status = '''
                    UPDATE guild_data 
                    SET disabled = (?) 
                    WHERE guild_id = (?)
                    '''
                    await self.bot.db.execute(update_cmd_status, (json.dumps(jso), str(ctx.guild.id),))
                    await self.fetchDisabled()
                    await ctx.send(jso)

            except Exception as e:
                print("Exception in disable:\n", e)

async def setup(bot):
    await bot.add_cog(Mod(bot))
