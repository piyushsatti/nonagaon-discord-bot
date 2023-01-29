from fastapi import APIRouter, HTTPException
from bot.bot import bot

router = APIRouter(
    prefix="/bot/guild"
)

@router.get('/state/{guild_id}')
async def bot_guild_state(guild_id):
    try:
        cur = await bot.db.execute("SELECT * FROM guild_data WHERE guild_id = ?", (str(guild_id),))
        return await cur.fetchone()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in bot_guild_state ---\n{e}")