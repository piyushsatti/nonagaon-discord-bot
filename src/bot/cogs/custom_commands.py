import discord
from discord.ext import commands

# Code Imports
from classes.colors import bcolors
from classes.base import Base

class Custom(Base, name="Custom Commands"):
    """Lets you create your own custom commands"""
    def __init__(self, bot):
        self.bot = bot

    async def get_prefix_(self, message):
        q = "SELECT guild_prefix FROM guild_data WHERE guild_id = ?"
        cur = await self.bot.db.execute(q, (str(message.guild.id),))
        prefix = await cur.fetchone()
        return prefix[0]

    @commands.command()
    async def setcommand(self, ctx, command, *, msg):

        if await self.command_disabled(ctx.command.cog_name, ctx.guild.id) != True:

            '''Sets a new custom command'''

            try:
                dbq = '''
                    INSERT OR REPLACE INTO custom_commands
                    (guild_id, command_name, message)
                    VALUES (?,?,?)
                '''
                await self.bot.db.execute(dbq, (str(ctx.guild.id), command, msg))
                await self.bot.db.commit()
            except Exception as e:
                print("Exception in setcommand:\n", e)

            embed = discord.Embed(
                color = self.bot.color,
                title = f"***Custom Command `{command}` now refers to `{msg}`.***"
            )
            await ctx.send(embed=embed)



    @commands.command()
    async def deletecustomcommand(self, ctx, command_name, message):
        '''Deletes a custom command'''
        if await self.command_disabled(ctx.command.cog_name, ctx.guild.id) != True:

            try:
                q = '''
                DELETE FROM custom_commands
                WHERE guild_id = (?) AND command_name = (?) AND message = (?)
                '''
                await self.bot.db.execute(q, (q, (ctx.guild.id, command_name, message)))
                await self.bot.db.commit()

                embed = discord.Embed(
                    color = self.bot.color,
                    title = f"***Custom Command `{command_name}` has been deleted.***"
                )
                await ctx.send(embed=embed)

            except Exception as e:
                print('Exception in deletecustomcommand:\n',e)

   
    @commands.command()
    async def listcustomcommands(self, ctx):
        '''Lists all the custom commands created'''
        if await self.command_disabled(ctx.command.cog_name, ctx.guild.id) != True:
            try:
                q = '''
                SELECT command_name, message FROM custom_commands
                WHERE guild_id = (?)
                '''
                res_ = await (await self.bot.db.execute(q,(ctx.guild.id,))).fetchall()

                embed = discord.Embed(
                color = self.bot.color,
                title = f"All custom commands for {ctx.guild.name}\n"
                )

                for res in res_:
                    embed.add_field(name=res[0], value=f"```{res[1]}```", inline=True)

                await ctx.send(embed=embed)
            except Exception as e:
                print('Exception in listcustomcommands:\n',e)

    @commands.Cog.listener()
    async def on_message(self, message):
        if await self.command_disabled("Custom", message.guild.id) != True:
            if not message.author.bot:
                msg = message.content
                prefix = await self.get_prefix_(message)
                if msg[0] == prefix:
                    cmd = msg[1:]
                    try:
                        cmdq = '''
                        SELECT command_name, message FROM custom_commands
                        WHERE guild_id = ? AND command_name = ?
                        '''
                        cur = await self.bot.db.execute(cmdq, (str(message.guild.id), cmd))
                        data = await cur.fetchone()
                    except Exception as e:
                        print("Error in on_message:\n",e)
                    if data is not None:
                        if msg[1:] == data[0]:
                            await message.channel.send(data[1])

async def setup(bot):
    try:
        custom_q = '''
            CREATE TABLE IF NOT EXISTS custom_commands (
            guild_id VARCHAR, 
            command_name VARCHAR, 
            message VARCHAR,
            PRIMARY KEY (guild_id, command_name))'''
        await bot.db.execute(custom_q)
    except Exception as e:
        print('Error in creating table: custom_commands\n', e)

    await bot.add_cog(Custom(bot))