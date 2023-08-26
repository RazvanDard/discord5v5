from settings_setup.setup import *
import os
from backend_classes.playerData import playerManager
from discord import app_commands
from backend_classes.commandLogger import *
from backend_classes.serverManager import *
bot.remove_command('help')

token = settings.get_bot_token()

async def load_cogs():
    startup_extensions = os.listdir("./cogs")

    for e in startup_extensions:
        if '.py' not in e:
            startup_extensions.remove(e)
    
    startup_extensions = [ext.replace('.py', '') for ext in startup_extensions]
    
    for extension in startup_extensions:
        try:
            await bot.load_extension(f"cogs.{extension}")
            print(f"Loaded extension {extension}")   
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n\t->{}'.format(extension, exc))
            
@bot.event
async def on_ready():    
    await load_cogs()
    
    await bot.tree.sync(guild=discord.Object(id=settings.get_server_id()))
    
    print("Bot is ready")

    try:
        await playerManager.load_players_from_json("player_data.json", debug = True)        
    except Exception as e:
        print(e)    
    finally:
        playerManager.add_players_from_guild(bot.get_guild(settings.get_server_id()), debug = True)
        playerManager.save_players_to_json("player_data.json")
    
    for i in range(0, settings.get_server_count()):
        serverManager.add_server()

@bot.event
async def on_member_join(member):
    playerManager.add_player(member)
    

bot.run(token)
