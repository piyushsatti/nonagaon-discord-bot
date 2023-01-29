import asyncio
import uvicorn
from fastapi import FastAPI
app = FastAPI()

# Routers
from api import guild
app.include_router(guild.router)
 
# Removing warnings
import warnings
warnings.simplefilter("ignore")

# project imports
from bot.bot import peppermint, bot

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(peppermint())
    await asyncio.sleep(5)

@app.on_event("shutdown")
def shutdown_event():
    print("API Shutting Down")

@app.get("/")
async def home():
    return "Homepage."

@app.get("bot/guilds")
async def get_bot_guilds():
    try:
        cur = await bot.db.execute("SELECT guild_id FROM guild_data")
        return [ele[0] for ele in await cur.fetchall()]
    except Exception as e:
        print("--- Exception in get_bot_guilds ---\n", e)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5001)