from settings_setup.setup import *
from discord import app_commands
import datetime
from backend_classes.game import *
from backend_classes.handlerImage import *
import asyncio 
from backend_classes.commandLogger import *
from backend_classes.serverManager import *
guild = discord.Object(id=settings.get_server_id())

class PickCog(commands.Cog):
    def __init__(self, client):
        self.client = client
  
    @app_commands.command(name="pick")
    async def pick(self, interaction: discord.Interaction, number: int) -> None:
        game = GameManager.get_game(interaction.channel)
        
        if game is None:
            # Handle case where no game is found
             return await interaction.response.send_message("No game is running here.", ephemeral=True)
        
        if game.game_state != GameState.TEAM_PICK_STAGE and game.game_state != GameState.MAP_PICK_STAGE:
            # Handle case where game is not in the team pick stage
            return await interaction.response.send_message("Game is not in pick stage", ephemeral=True)
       

        if interaction.user == game.player_turn:
            if game.game_state == GameState.TEAM_PICK_STAGE:
                team_to_modify = game.team_red if interaction.user == game.captain_red else game.team_blue
                
                if number <= 0 or number > len(game.waiting_players):
                    # Handle invalid player number
                    return await interaction.response.send_message("Invalid player number", ephemeral=True)
                
                selected_player = game.waiting_players[number - 1]
                
                if(selected_player == -1):
                    # Handle case where selected player is already picked
                    return await interaction.response.send_message("Player was already picked", ephemeral=True)

                    
                team_to_modify.append(selected_player)
                game.waiting_players[number - 1] = -1 # we do this so that the numbers remain the same
                
                if(all(element == -1 for element in game.waiting_players)):
                    game.game_state = GameState.MAP_PICK_STAGE
                    return    await GameManager.update_embed(game)
                
            elif game.game_state == GameState.MAP_PICK_STAGE:
                if number <= 0 or number > len(game.map_pool):
                    # Handle invalid map number
                    return await interaction.response.send_message("Invalid map number", ephemeral=True)
                
                selected_map = game.map_pool[number - 1]
                
                if(selected_map == -1):
                    # Handle case where selected map is already picked
                    return await interaction.response.send_message("Map was already vetoed", ephemeral=True)
                
                game.map_pool[number - 1] = -1
               
                left_maps = [game_map for game_map in game.map if game_map != -1]
                # if the map has been picked, and there is only one map left in the map pool
                # then the game is ready to start
                if(len(left_maps) == 1):
                    game.game_state = GameState.PLAY_STAGE
                    
                    game.map = left_maps[0]
                    
                    return await GameManager.update_embed(game)
                
            # Switch player turn
            
            game.player_turn = game.captain_blue if game.player_turn == game.captain_red else game.captain_red
            
            await GameManager.update_embed(game)
             
        else:
            # Handle case where user is not the current captain's turn
            return await interaction.response.send_message("bruh not ur turn", ephemeral=True)

    
    @app_commands.command(name="forcecaptains")
    async def force_captains(self, interaction: discord.Interaction, captain_red: discord.Member, captain_blue: discord.Member ) -> None:
        game = GameManager.get_game(interaction.channel)
        
        if game is None:
            # Handle case where no game is found
                return await interaction.response.send_message("No game is running here.", ephemeral=True)
        
        if game.game_state != GameState.TEAM_PICK_STAGE:
            # Handle case where game is not in the team pick stage
            return await interaction.response.send_message("Game is not in team pick stage", ephemeral=True)
        
        if interaction.user != game.hoster:
            # Handle case where user is not the hoster
            return

        for player in game.team_blue:
            game.team_blue.remove(player)
            game.waiting_players.append(player)
            
        for player in game.team_red:
            game.team_red.remove(player)
            game.waiting_players.append(player)
            
        game.captain_blue = captain_blue
        game.captain_red = captain_red
        

        game.waiting_players.remove(captain_blue)   
        game.waiting_players.remove(captain_red)
     
        game.team_blue.append(game.captain_blue)
        game.team_red.append(game.captain_red)
    
        game.player_turn = captain_red
        
        await GameManager.update_embed(game)
        
        await commandLogger.log(f"{interaction.user.display_name} has force set captains for Game #{game.id} in {interaction.channel}.", interaction.user)
        
              
    @app_commands.command(name="redraft")
    async def redraft(self, interaction: discord.Interaction) -> None:
        game = GameManager.get_game(interaction.channel)
        
        if game is None:
            # Handle case where no game is found
                return await interaction.response.send_message("No game is running here.", ephemeral=True)
        
        if game.game_state != GameState.TEAM_PICK_STAGE:
            # Handle case where game is not in the team pick stage
            return await interaction.response.send_message("Game is not in team pick stage", ephemeral=True)
        
        if interaction.user != game.hoster:
            # Handle case where user is not the hoster
            return

        for player in game.team_blue:
            game.team_blue.remove(player)
            game.waiting_players.append(player)
            
        for player in game.team_red:
            game.team_red.remove(player)
            game.waiting_players.append(player)
            
        game.captain_blue = None
        game.captain_red = None
  
        await GameManager.update_embed(game)
        
        await commandLogger.log(f"{interaction.user.display_name} has redrafted Game #{game.id} in {interaction.channel}.", interaction.user)

    @app_commands.command(name="replace")
    async def replace(self, interaction: discord.Interaction, old_player: discord.Member, new_player: discord.Member) -> None:
        if not playerManager.get_player(interaction.user).has_hoster_perms():
            # Handle case where user does not have hoster perms
            return await interaction.response.send_message("You do not have hoster perms.", ephemeral=True)
        
        game = GameManager.get_game(interaction.channel)
        
        if game is None:
            # Handle case where no game is found
            return await interaction.response.send_message("No game is running here", ephemeral=True)
        
        if game.game_state != GameState.PLAY_STAGE and game.game_state != GameState.MAP_PICK_STAGE and game.game_state != GameState.TEAM_PICK_STAGE:
            # Handle case where game is not in the play stage or map pick stage
            return await interaction.response.send_message("Can't replace a player now", ephemeral=True)

        if interaction.user != game.hoster:
            # Handle case where user is not the hoster
            return
        
        try:
            game.replace_player(old_player, new_player)
            await GameManager.update_embed(game)
        except Exception as e:
            # Handle exceptions raised from replace_player.
            return await interaction.response.send_message(str(e), ephemeral=True)
        
        await commandLogger.log(f"{interaction.user.display_name} has replaced {old_player.display_name} with {new_player.display_name} in Game #{game.id} in {interaction.channel}.", interaction.user)
        
        await game.update_player_roles()
        
        await serverManager.send_password(game.server, new_player)
           
        


async def setup(bot):
    await bot.add_cog(PickCog(bot), guild=guild)

