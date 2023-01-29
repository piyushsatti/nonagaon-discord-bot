from cgitb import text
import discord, asyncio, os, aiosqlite, DiscordUtils, json
from discord.ext import commands
from pretty_help import PrettyHelp

# system pathing
import sys, os
sys.path.append(
    os.path.join(
        os.getcwd(),
        'src',
        'bot'
    )
)

async def get_prefix(bot, message):
    try:
        cur = await bot.db.execute("SELECT guild_prefix FROM guild_data WHERE guild_id = ?", (str(message.guild.id),))
        return await cur.fetchone()
    except Exception as e:
        print("Exception in Get Prefix:\n", e)
        return "Failed to get prefix from DB"

owners = [798970247653621810]
bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents().all(), owner_ids = set(owners), help_command=PrettyHelp(color=0xe86f52, sort_commands=True, show_index=True, no_category=None ))

bot.multiplier = 1
bot.color = 0xe86f52
bot.disabled = {}

async def load_extensions():
    path_to_cogs = os.path.join(os.getcwd(), 'src', 'bot', 'cogs')
    for fn in os.listdir(path_to_cogs):
        if fn.endswith(".py"):
            await bot.load_extension(f"cogs.{fn[:-3]}")
            print(f"Loaded cog {fn}!")

async def fetchDisabled():
    fetch_cmd_status = '''
    SELECT disabled 
    FROM guild_data
    WHERE guild_id = (?)
    '''

    for guild in bot.guilds:
        cur =  await bot.db.execute(fetch_cmd_status, (str(guild.id),))
        res = await cur.fetchone()
        jso = json.loads(res[0])

        bot.disabled[str(guild.id)] = jso
        
'''
        for guild in bot.guilds:
            for cog in bot.cogs:
                if not bot.disabled[str(guild.id)][cog]:
                    bot.disabled[str(guild.id)][cog] = 'True'

        print(bot.disabled)
'''

@commands.is_owner()
@bot.command(hidden=True) 
async def load(ctx, extension):
    await bot.load_extension(f"bot.cogs.{extension}")
    await ctx.send(f"Loaded {extension}!")

@commands.is_owner()
@bot.command(hidden=True) 
async def history(ctx):
    async for message in ctx.channel.history(limit=1):
        try:
            print(dir(message))
        except Exception as E:
            print(E)

@commands.is_owner()
@bot.command(hidden=True)
async def unload(ctx, extension):
    await bot.unload_extension(f"bot.cogs.{extension}")
    await ctx.send(f"Unloaded {extension}!")

@commands.is_owner()
@bot.command(hidden=True)
async def reload(ctx, extension):
    await bot.reload_extension(f"bot.cogs.{extension}")
    await ctx.send(f"Reloaded {extension}!")

@bot.event
async def on_ready():
    await fetchDisabled()

async def peppermint():
    async with bot:

        path_to_db = os.path.join(os.getcwd(), 'db', 'peppermint.db')
        bot.db = await aiosqlite.connect(path_to_db)
        bot.tracker = DiscordUtils.InviteTracker(bot)
  

        try:

            
            # await bot.db.execute('''DROP TABLE guild_data;''')
            guild_q = '''CREATE TABLE IF NOT EXISTS guild_data (
                guild_id VARCHAR, 
                stat_channel_id VARCHAR, 
                welcome_channel_id VARCHAR,
                guild_prefix VARCHAR DEFAULT '!',
                disabled VARCHAR DEFAULT '{}', 
                PRIMARY KEY (guild_id))'''
            await bot.db.execute(guild_q)
            await bot.db.commit()

        except Exception as e:
            print('Error in creating table: guild_data\n', e)

        await load_extensions()
        await bot.start('ODk4NTYzODIzNDIwNzM1NTU4.YWmCxg.XLhADtRS_67LwqmFuhDu2GDDRDA')
        

if __name__ == "__main__":
    asyncio.run(peppermint())