from discord import app_commands
from discord.ext import commands
import discord
import datetime
import asyncio
from backend_classes.game import GameManager  # You might need to adjust the import paths
from backend_classes.playerData import playerManager  # Adjust the import path for playerManager
from settings_setup.setup import settings
from backend_classes.commandLogger import *
guild = discord.Object(id=settings.get_server_id())  # Adjust the guild ID if necessary

class EloCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @app_commands.command(name="addelo")
    async def addelo(self, interaction: discord.Interaction, user: discord.User, amount: int) -> None:
        player = playerManager.get_player(user)
        
        if player.has_mod_perms():
            player.add_elo(amount)
            await interaction.response.send_message(f"Added {amount} Elo to {user.display_name}.", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            
        await commandLogger.log(f"{interaction.user.display_name} has added {amount} Elo to {user.display_name}.", interaction.user)
    
    @app_commands.command(name="removeelo")
    async def removeelo(self, interaction: discord.Interaction, user: discord.User, amount: int) -> None:
        player = playerManager.get_player(user)
        
        if player.has_mod_perms():
            player.remove_elo(amount)
            await interaction.response.send_message(f"Removed {amount} Elo from {user.display_name}.", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        
        await commandLogger.log(f"{interaction.user.display_name} has removed {amount} Elo from {user.display_name}.", interaction.user)
    
    @app_commands.command(name="addwin")
    async def addwin(self, interaction: discord.Interaction, user: discord.User) -> None:
        player = playerManager.get_player(user)
        
        if player.has_mod_perms():
            player.add_win()
            await interaction.response.send_message(f"Added a win for {user.display_name}.", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            
        await commandLogger.log(f"{interaction.user.display_name} has added a win for {user.display_name}.", interaction.user)
    
    @app_commands.command(name="removewin")
    async def removewin(self, interaction: discord.Interaction, user: discord.User) -> None:
        player = playerManager.get_player(user)
        
        if player.has_mod_perms():
            player.remove_win()
            await interaction.response.send_message(f"Removed a win from {user.display_name}.", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            
        await commandLogger.log(f"{interaction.user.display_name} has removed a win from {user.display_name}.", interaction.user)
    
    @app_commands.command(name="addlose")
    async def addlose(self, interaction: discord.Interaction, user: discord.User) -> None:
        player = playerManager.get_player(user)
        
        if player.has_mod_perms():
            player.add_lose()
            await interaction.response.send_message(f"Added a loss for {user.display_name}.", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            
        await commandLogger.log(f"{interaction.user.display_name} has added a loss for {user.display_name}.", interaction.user)
    
    @app_commands.command(name="removelose")
    async def removelose(self, interaction: discord.Interaction, user: discord.User) -> None:
        player = playerManager.get_player(user)
        
        if player.has_mod_perms():
            player.remove_lose()
            await interaction.response.send_message(f"Removed a loss from {user.display_name}.", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            
        await commandLogger.log(f"{interaction.user.display_name} has removed a loss from {user.display_name}.", interaction.user)
    
    
    @app_commands.command(name="resetleaderboard")
    async def reset_leaderboard(self, interaction: discord.Interaction) -> None:
        if(playerManager.get_player(interaction.user).has_admin_perms()):
            playerManager.reset_leaderboard()
            await interaction.response.send_message("Leaderboard has been reset.", ephemeral=True)
            
        await commandLogger.log(f"{interaction.user.display_name} has reset the leaderboard.", interaction.user)
        
        playerManager.save_players_to_json("player_data.json")
    # Other methods and utilities for the EloCog can go here

async def setup(bot):
    await bot.add_cog(EloCog(bot), guild=guild)
