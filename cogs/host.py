from settings_setup.setup import *
from discord import app_commands
import datetime
from backend_classes.game import *
from backend_classes.handlerImage import *
import asyncio 
from backend_classes.commandLogger import *
guild = discord.Object(id=settings.get_server_id())

class Host(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @app_commands.command(name="host")
    async def host(self, interaction: discord.Interaction) -> None:
        if(not playerManager.get_player(interaction.user).has_hoster_perms()): 
            return await interaction.response.send_message("You do not have hoster perms.", ephemeral=True)
            
        if(GameManager.get_game(interaction.channel) is not None):
            return await interaction.response.send_message("Game is already running here.", ephemeral=True)
        
        if(not (interaction.channel.id in settings.get_hosting_channels())):
            return await interaction.response.send_message("You can not host here.", ephemeral=True)
        
        game = GameManager.add_game(interaction.user, interaction.channel)
        
        embed = discord.Embed(title = 'Players in lobby', 
                              description=f"**Game #{game.id} has begun! Type /join**\n```css\n[Waiting for players to join]```",
                              color=discord.Color.dark_orange(), timestamp=datetime.datetime.utcnow())
        
        embed.set_footer(text=f'Hosted by {interaction.user.display_name}', icon_url=interaction.user.avatar.url or interaction.user.default_avatar.url)
    
        game.embed = await interaction.channel.send(embed=embed)
        await commandLogger.log(f"{interaction.user.display_name} has started Game #{game.id} in {interaction.channel}.", interaction.user)
        await interaction.response.send_message("You are hosting!!", ephemeral=True)

    @app_commands.command(name="cancel")
    async def cancel(self, interaction: discord.Interaction) -> None:
        player = playerManager.get_player(interaction.user)
        
        if not player.has_hoster_perms():
            return await interaction.response.send_message("You do not have hoster perms.", ephemeral=True)
        
        game = GameManager.get_game(interaction.channel)
        
        if not game:
            return await interaction.response.send_message("No game is running here.", ephemeral=True)
        
        if game.game_state == GameState.PLAY_STAGE:
            return await interaction.response.send_message("Cannot cancel a game in play stage.", ephemeral=True)
        
        GameManager.remove_game(game)
        
        await commandLogger.log(f"{interaction.user.display_name} has canceled Game #{game.id} in {interaction.channel}.", interaction.user)
        await game.embed.delete()
        
        await interaction.response.send_message("Game has been canceled", ephemeral=True)
        await interaction.channel.send("Game has been cancelled.")
        
        
        
    @app_commands.command(name="forcecancel")
    async def forcecancel(self, interaction: discord.Interaction) -> None:
        player = playerManager.get_player(interaction.user)
        
        if not player.has_mod_perms():
            return await interaction.response.send_message("You do not have mod perms.", ephemeral=True)
        
        game = GameManager.get_game(interaction.channel)
        
        if not game:
            return await interaction.response.send_message("No game is running here.", ephemeral=True)
        
        GameManager.remove_game(game)
        
        try:
            await game.embed.delete()
        except:
            pass
        
        try:
            await game.start_image.delete()
        except:
            pass
        
        await commandLogger.log(f"{interaction.user.display_name} has force canceled Game #{game.id} in {interaction.channel}.", interaction.user)
      
        await interaction.response.send_message("Game has been canceled", ephemeral=True)
        await interaction.channel.send("Game has been cancelled.")
        
    @app_commands.command(name="forcestart")
    async def forcestart(self, interaction: discord.Interaction) -> None:
        if(not playerManager.get_player(interaction.user).has_admin_perms()):
            return await interaction.response.send_message("You do not have admin perms.", ephemeral=True)
        
        game = GameManager.get_game(interaction.channel)
        
        if not game:
            return await interaction.response.send_message("No game is running here.", ephemeral=True)
        
        await interaction.response.send_message("You have forcestarted the game.", ephemeral=True)
        
        for player in game.waiting_players:
            team = min(game.team_red, game.team_blue, key=len)
            
            team.append(player)
                    
            await asyncio.sleep(1)
            await GameManager.update_embed(game)

        await asyncio.sleep(1)
        game.waiting_players = []
        
        game.game_state = GameState.MAP_PICK_STAGE
        await GameManager.update_embed(game)
        
        await asyncio.sleep(1)
        
        game.map_pool = ["de_mirage"]
        game.map = "de_mirage"
        
        await GameManager.update_embed(game)
        
        await asyncio.sleep(1)
        
        game.game_state = GameState.PLAY_STAGE
        await GameManager.update_embed(game)
        
    @app_commands.command(name="game")
    async def game(self, interaction: discord.Interaction, winning_team: str) -> None:
        game = GameManager.get_game(interaction.channel)
        
        if not game:
            return await interaction.response.send_message("No game is running here.", ephemeral=True)
        
        if game.game_state != GameState.PLAY_STAGE:
            return await interaction.response.send_message("Game is not in play stage.", ephemeral=True)
        
        player = playerManager.get_player(interaction.user)
        
        if(not player.has_hoster_perms() or not (interaction.user in game.players or player.has_mod_perms())):
            return await interaction.response.send_message("You do not access to end this game.", ephemeral=True)
        
        if(not(winning_team.lower() in ["1","2","tie"])):
            return await interaction.response.send_message("Invalid team name. Try 1/2/tie", ephemeral=True)
        
        await interaction.response.send_message(f"Team {winning_team} has won", ephemeral=True)
        
        game.set_winner(winning_team)
        
        await GameManager.finish_game(game)
        
        if(winning_team.lower() == "tie"):
            return await interaction.channel.send("Game has been tied.")
        
        win_image, lose_image = GameManager.generate_end_image(game)
        
        game.end_image.append(await interaction.channel.send(file = win_image))
        
        await asyncio.sleep(0.5)
        
        game.end_image.append(await interaction.channel.send(file = lose_image))
        
        playerManager.save_players_to_json("player_data.json")
        
        await commandLogger.log(f"{interaction.user.display_name} has ended Game #{game.id} in {interaction.channel}.Set winning team as {winning_team}", interaction.user)
        
            
async def setup(bot):
    await bot.add_cog(Host(bot), guild=guild)

