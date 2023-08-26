import discord
import json
from settings_setup.setup import *
import datetime

class Logger():
    def __init__(self):
        self.channel = None
        self.log_file = "logs.json"
        
    async def log(self, message, author = None, *, params = None):
        if self.channel is None:
            self.channel = await bot.fetch_channel(settings.get_log_channel_id())
            
        await self.channel.send(message)
        
        self.append_log_to_file(message,author = author, params = params)
        print(f"Logged message: {message}")
        
    def append_log_to_file(self, message, author = None,*, params = None):
        log_data = {
            "timestamp"   : str(datetime.datetime.utcnow()),
            "message"     : message,
            "author_id"   : author.id if author else None,
            "params"      : params
        }
        
        with open(self.log_file, "a") as file:
            json.dump(log_data, file)
            file.write("\n")


commandLogger = Logger()

