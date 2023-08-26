from settings_setup.setup import *
from discord import app_commands
import datetime
from backend_classes.game import *
from backend_classes.handlerImage import *
import asyncio 
import math
from backend_classes.playerData import *

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
       
    
    async def update_leaderboard(self):
        playerManager.update_leaderboard()
    
    async def save_players(self):
        playerManager.save_players_to_json("player_data.json")
        
    @app_commands.command(name="leaderboard")
    async def leaderboard(self, interaction: discord.Interaction, page: int = 1):
        await interaction.response.send_message("Updating leaderboard...")
        
        await self.update_leaderboard()
        # await self.save_players()

        page = max(1, page)
        player_list = playerManager.get_leaderboard()
        str_1 = ''
        player_per_page = 10

        if (type((len(player_list)) / player_per_page) != int):
            pages = math.ceil(len(player_list) / player_per_page)
        else:
            pages = (len(player_list)) / player_per_page

        if (page > pages and pages > 1):
            return await interaction.followup.send(f"I'm afraid there's only {pages} pages")
        if (page > pages and pages == 1):
            return await interaction.followup.send(f"I'm afraid there's only {pages} page")

        for y in range(player_per_page * page - player_per_page, player_per_page * page):
            try:
                int_elo = int(player_list[y].rating)
            except:
                await interaction.followup.send(f'There is not {page} pages!')
            try:
                appname = player_list[y].discord_user.display_name[0:12]
            except:
                appname = '?_-_?'

            remainder = 6 - len(appname)
            remainder1 = 6 - len(str(player_list[y].rating))
            remainder2 = 2 - len(str(player_list[y].games_won))
            remainder3 = 2 - len(str(player_list[y].games_lost))

            if y == 9:
                remainder = remainder - 1
            str_1 += f"{str(y + 1)}. {appname}" + ''.join(' ' for i in range(11 + remainder)) + \
                    f'{str(player_list[y].rating)}' + ''.join(' ' for i in range(2 + remainder1)) + \
                    f'  {str(player_list[y].games_won)}' + ''.join(' ' for i in range(5 + remainder2)) + \
                    f' {str(player_list[y].games_lost)}' + ''.join(' ' for i in range(4 + remainder3)) + \
                    f'{str(player_list[y].win_streak)}\n'

        embed = discord.Embed(title=f"Leaderboard Ranks", color=discord.Color.dark_orange())
        embed.description = ('```ini\nRank Player         Elo      Wins  Losses Streak\n``` \n' +
                            f"```ini\n{str_1}```")
        
        if interaction.user.avatar is None:
            embed.set_footer(text=f'{interaction.user.display_name} - Commander')
        else:
            embed.set_footer(text=f'{interaction.user.display_name} - Commander', icon_url=interaction.user.avatar.url)
            
        await interaction.followup.send(embed=embed)
        
    @app_commands.command(name="stats")
    async def stats(self, interaction: discord.Interaction, user: discord.User = None):
        await self.update_leaderboard()  # Assuming you have defined this function
        
        user = interaction.user if not user else user
          
        player = playerManager.get_player(user)
        
        if player is None:
            return await interaction.response.send_message("Player not found.", ephemeral=True)
    
        embed = discord.Embed(title="Stats", color=discord.Color.dark_orange())
        embed.description = (
            f"Target: {user.mention}\nRank: {player.leaderboard_rank}\n"
            f"Elo: {player.rating}\nWins: {player.games_won}\nLosses: {player.games_lost}\nStreak: {player.win_streak}"
        )
        if user.avatar is None:
            embed.set_footer(text=f"{user.display_name} - Commander")
        else:
            embed.set_thumbnail(url=user.avatar.url)
            embed.set_footer(text=f"{user.display_name} - Commander", icon_url=user.avatar.url)
        
        # You might want to set the image URL correctly based on your use case
        # rank_url = "URL_TO_RANK_IMAGE"
        # embed.set_image(url=rank_url)

        await interaction.response.send_message(embed=embed, ephemeral=True)



guild = discord.Object(id=settings.get_server_id())

async def setup(bot):
    await bot.add_cog(LeaderboardCog(bot), guild=guild)

