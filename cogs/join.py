from settings_setup.setup import *
from discord import app_commands
import datetime
from backend_classes.game import *
from backend_classes.handlerImage import *
import asyncio 
from cogs.blacklist import blackListUtils
from backend_classes.commandLogger import *
from backend_classes.serverManager import *
guild = discord.Object(id=settings.get_server_id())

class Join(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @app_commands.command(name="join")
    async def join(self, interaction: discord.Interaction) -> None:
        game = GameManager.get_game(interaction.channel)
        
        if game is None:
            # Handle case where no game is found
             return await interaction.response.send_message("No game is running here.", ephemeral=True)
        
        if blackListUtils.is_blacklisted(interaction.user):
  
            return await interaction.response.send_message(f"You are blacklisted for {blackListUtils.get_remaining_time(interaction.user)}", ephemeral=True)
        
        
        if game.game_state != GameState.JOIN_STAGE:
            # Handle case where game is not in the team pick stage
            return await interaction.response.send_message("This game has already started", ephemeral=True)
        
        if interaction.user in game.players:
            # Handle case where player is already in the game
            return await interaction.response.send_message("You are already in the game.", ephemeral=True)
        
        
        try:
            game.add_player(interaction.user)
            await GameManager.update_embed(game)
        except Exception as e:
            if(e == "Game is full."):
                return await interaction.response.send_message(str(e), ephemeral=True)
            else:
                await GameManager.update_embed(game)

        await interaction.response.send_message("You have joined.", ephemeral=True)
    
    @app_commands.command(name="leave")
    async def leave(self,  interaction: discord.Interaction) -> None:
        game = GameManager.get_game(interaction.channel)

        if game is None:
            # Handle case where no game is found
            return await interaction.response.send_message("No game is running here.", ephemeral=True)
        
        if interaction.user not in game.players:
            # Handle case where player is not in the game
            return await interaction.response.send_message("You are not in the game.", ephemeral=True)
        
        if game.game_state != GameState.JOIN_STAGE:
            # Handle case where game is not in the team pick stage
            return await interaction.response.send_message("This game has already started", ephemeral=True)
        
        game.remove_player(interaction.user)
        
        await GameManager.update_embed(game)
        
        return await interaction.response.send_message("You have left.", ephemeral=True)
        
    @app_commands.command(name="password")
    async def password(self, interaction: discord.Interaction) -> None:
        game = GameManager.get_game(interaction.channel)
        
        await serverManager.send_password(game.server, interaction.user)
        
        return await interaction.response.send_message("Password sent. Check DM.", ephemeral=True)
    @app_commands.command(name="forcejoin")
    async def forcejoin(self, interaction: discord.Interaction, user: discord.User) -> None:
        
        if(not playerManager.get_player(interaction.user).has_mod_perms()):
            return await interaction.response.send_message("You do not have mod perms.", ephemeral=True)
        
        game = GameManager.get_game(interaction.channel)
             
        if user in game.players:
            # Handle case where player is already in the game
            return await interaction.response.send_message("You are already in the game.", ephemeral=True)
                
        try:
            game.add_player(user)
            await GameManager.update_embed(game)
        except Exception as e:
            if(e == "Game is full."):
                return await interaction.response.send_message(str(e), ephemeral=True)
            else:
                   await GameManager.update_embed(game)
        
        await commandLogger.log(f"{interaction.user}[{interaction.user.display_name}] has force joined {user}[{user.display_name}] in {interaction.channel}")
        await interaction.response.send_message("You have joined.", ephemeral=True)
        
    @app_commands.command(name="forcejoinmass")
    async def forcejoinmass(self, interaction: discord.Interaction) -> None:
        if(not playerManager.get_player(interaction.user).has_admin_perms()):
            return await interaction.response.send_message("You do not have admin perms.", ephemeral=True)
        
        game = GameManager.get_game(interaction.channel)
        
        await interaction.response.send_message("You have mass force joined.", ephemeral=True)
        
        for user in interaction.guild.members:
            if(user.bot or user in game.players):
                continue
            
            if(game.is_full):
                return 
            try:
                game.add_player(user)
                await GameManager.update_embed(game)
            except Exception as e:
                if(e == "Game is full."):
                    return await interaction.followup.send_message(str(e), ephemeral=True)
                else:
                    await GameManager.update_embed(game)
                    
            await asyncio.sleep(1)
        
        await commandLogger.log(f"{interaction.user}[{interaction.user.display_name}] has mass force joined in {interaction.channel}")
            
        
            
async def setup(bot):
    await bot.add_cog(Join(bot), guild=guild)

