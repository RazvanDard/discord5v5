from discord.ext import commands
import discord
import re
import datetime
from discord import app_commands
import asyncio
from backend_classes.playerData import *
from backend_classes.commandLogger import *
class BlackListUtilities():
    def __init__(self):
        pass
    
    def convert_duration(self, duration_str):
        # Parse the input string like "6d", "1h", "30m" to a datetime
        duration_match = re.match(r'(\d+)([dhm])', duration_str)
        if duration_match:
            amount = int(duration_match.group(1))
            unit = duration_match.group(2)
            if unit == 'd':
                return datetime.timedelta(days=amount)
            elif unit == 'h':
                return datetime.timedelta(hours=amount)
            elif unit == 'm':
                return datetime.timedelta(minutes=amount)
        return None

     # Check if a user is blacklisted before running a command
    def is_blacklisted(self, user: discord.User):
        player = playerManager.get_player(user)
        if player.blacklist_time and datetime.datetime.utcnow() < player.blacklist_time:
            return True
        else:
            player.blacklist_time = None
            return False
        
    def blacklist_player(self, user: discord.User, duration: datetime.timedelta):
        player = playerManager.get_player(user)
        player.blacklist_time = datetime.datetime.utcnow() + duration
        
    def whitelist_player(self, user: discord.User):
        player = playerManager.get_player(user)
        player.blacklist_time = None
    
    def get_remaining_time(self, user: discord.user):
        player = playerManager.get_player(user)
        
        if player.blacklist_time != None:
            remaining_duration = player.blacklist_time - datetime.datetime.utcnow()
            days, seconds = remaining_duration.days, remaining_duration.seconds
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            time_parts = []
            if days > 0:
                time_parts.append(f"{days} day{'s' if days > 1 else ''}")
            if hours > 0:
                time_parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
            if minutes > 0:
                time_parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
            if seconds > 0:
                time_parts.append(f"{seconds} second{'s' if seconds > 1 else ''}")
            
            remaining_time_str = " and ".join(time_parts)
            
            return remaining_time_str
        else:
            return "You are not blacklisted."
    
blackListUtils = BlackListUtilities()

class Blacklist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
      
    
    @app_commands.command(name="blacklist")
    async def blacklist_user(self, interaction: discord.Interaction, user: discord.User, duration: str):
        """Blacklist a user for a specified duration (e.g., 6d, 1h, 30m)"""
     
        if not playerManager.get_player(interaction.user).has_mod_perms():
            return await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
     
        expire_duration = blackListUtils.convert_duration(duration)
        if not expire_duration:
            return await interaction.response.send_message("Invalid duration format. Use e.g., 6d, 1h, 30m.", ephemeral=True)
     
        blackListUtils.blacklist_player(user, expire_duration)
        
        playerManager.save_players_to_json("player_data.json")
        
        await commandLogger.log(f"{interaction.user.display_name} has blacklisted {user.display_name} for {duration}", interaction.user)
        return await interaction.response.send_message(f"Blacklisted {user.display_name} for {duration}.", ephemeral=True)
    
    @app_commands.command(name="whitelist")
    async def whitelist_user(self, interaction: discord.Interaction, user: discord.User):
        """Whitelist a user"""
     
        if not playerManager.get_player(interaction.user).has_mod_perms():
            return await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

        if not blackListUtils.is_blacklisted(user):
            return await interaction.response.send_message(f"{user.display_name} is not blacklisted.", ephemeral=True)
        
        blackListUtils.whitelist_player(user)
        
        playerManager.save_players_to_json("player_data.json")
        
        await commandLogger.log(f"{interaction.user.display_name} has whitelisted {user.display_name}", interaction.user)
        return await interaction.response.send_message(f"Whitelisted {user.display_name}.", ephemeral=True)
        
        
    

guild = discord.Object(id=settings.get_server_id())

async def setup(bot):
    await bot.add_cog(Blacklist(bot), guild=guild)
