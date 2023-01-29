from fastapi import APIRouter, HTTPException
from bot.bot import bot

router = APIRouter(
    prefix="/bot/guild"
)

@app.get('/guild/custom-commands/{guild_id}')
async def getGuildFunc(guild_id):
    try:
        cur = await bot.db.execute("SELECT * FROM custom_commands WHERE guild_id = ?", (str(guild_id),))
        return await cur.fetchall()
    except Exception as e:
        print("Exception in Get Prefix:\n", e)
        return "Failed to get prefix from DB"