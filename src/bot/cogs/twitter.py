import json, tweepy, asyncio, threading
from discord.ext import commands, tasks
from discord_webhook import DiscordWebhook

# Code Imports
from classes.colors import bcolors
from classes.base import Base

# Reading from Project Config File
from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")

# Config File loading
CONSUMER_KEY         =   config['twitter']['CONSUMER_KEY']
CONSUMER_SECRET      =   config['twitter']['CONSUMER_SECRET']
ACCESS_TOKEN         =   config['twitter']['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET  =   config['twitter']['ACCESS_TOKEN_SECRET']
TEST_LIST            =   json.loads(config['twitter']['USERS'])

class Twitter(Base, name="Twitter"):
    """Integrates your twitter account with the bot"""
    def __init__(self, bot):
        self.bot = bot
        twitter_thread = threading.Thread(target=self.tweepyListener)
        twitter_thread.start()

    def tweepyListener(self):
        stream = MyStreamListener(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        stream.filter(follow=TEST_LIST)

# Overwritten Stream listener
class MyStreamListener(tweepy.Stream):

    async def on_status(self, status):
        tweet_attr = status._json
        if not tweet_attr['retweeted'] and 'RT @' not in tweet_attr['text']:
            if self.from_creator(status):
                webhook = DiscordWebhook(url=DISCORD_WEBHOOK, content=status.text).execute()

    # checks if from creator
    async def from_creator(self, status):
            if hasattr(status, 'retweeted_status'):
                return False
            elif status.in_reply_to_status_id != None:
                return False
            elif status.in_reply_to_screen_name != None:
                return False
            elif status.in_reply_to_user_id != None:
                return False
            else:
                return True

    async def on_error(self, status_code):
        if status_code == 420:  # end of monthly limit rate (500k)
            return False

### Bot Setup ###
async def setup(bot):
    try: 
        q = '''
            CREATE TABLE IF NOT EXISTS twitter (
            guild_id VARCHAR,
            tweet_send_to_channel_id VARCHAR,
            twitter_user_id VARCHAR, 
            PRIMARY KEY (guild_id))
            '''
        await bot.db.execute(q)
    except Exception as e:
        print('Error in creating table: twitter\n', e)

    await bot.add_cog(Twitter(bot))

if __name__ == '__main__':
    import requests
    # getting user-id from user-tag
    a = requests.post('https://tweeterid.com/ajax.php', data={'input':'@randomtweetsapp'})
    print(a._content)