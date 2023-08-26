from dataclasses import dataclass
import discord 
from enum import Enum
from backend_classes.handlerImage import *
import datetime
from settings_setup.setup import *
import random
from backend_classes.playerData import *
from backend_classes.serverManager import *
import asyncio
class GameState(Enum):
    JOIN_STAGE = 1
    TEAM_PICK_STAGE = 2
    MAP_PICK_STAGE = 3
    PLAY_STAGE = 4
    END_GAME = 5

@dataclass
class Game:
    id: int 
    hoster: discord.User
    channel: discord.TextChannel
    players: list[discord.User]
    waiting_players: list[discord.User]
    
    player_turn: discord.User = None
    
    team_red: list[discord.User] = None
    team_blue: list[discord.User] = None
    
    map_pool: list[str] = None
    map: str = None
    
    captain_red: discord.User = None
    captain_blue: discord.User = None
    
    server: Server = None
    
    game_state: GameState = GameState.JOIN_STAGE
    is_finished: bool = False
    
    start_image: discord.Message = None
    end_image: list[discord.Message] = None
    
    is_full: bool = False
    max_players: int = 10
    embed: discord.Embed = None
    
    def __init__(self, hoster, channel, id):
        self.hoster = hoster
        self.id = id
        self.channel = channel
        self.players = []
        self.waiting_players = []
        self.team_red = []
        self.team_blue = []
        self.end_image = []
        self.winning_team = []
        self.losing_team = []
        
        print(self.channel.id)
        self.map_pool = settings.get_5v5_maps()
       
      
    
    def add_player(self, player: discord.User):
        if(len(self.players) >= self.max_players):
            raise Exception("Game is full.")
        
        self.players.append(player)
        self.waiting_players.append(player)
        
        if(len(self.players) == self.max_players):
            self.is_full = True
            self.game_state = GameState.TEAM_PICK_STAGE
            
            raise Exception("Enter team pick stage.")
        
    
    def remove_player(self, player: discord.User, * , force_remove: bool = False):
        if(self.game_state != GameState.JOIN_STAGE and not force_remove):
            raise Exception("Cannot remove player in this game state. Try replacing the player.")
        
        if(self.is_full):
            self.is_full = False
        
        if(player not in self.players):
            raise Exception("Player not found in game.")
        
        self.players.remove(player)
        
        if(player in self.waiting_players):
            self.waiting_players.remove(player)
        
    def replace_player(self, old_player: discord.User, new_player: discord.User):  
        if(self.game_state != GameState.PLAY_STAGE and self.game_state != GameState.MAP_PICK_STAGE and self.game_state != GameState.TEAM_PICK_STAGE):   
            raise Exception("Cannot replace player in this game state.")
        
        if(old_player not in self.players):
            raise Exception("Player not found in game.")
        
        self.players.remove(old_player)
        self.players.append(new_player)
        
        team: list[discord.User] = []
        
        if(old_player in self.team_red):
            team = self.team_red
        elif(old_player in self.team_blue):
            team = self.team_blue
        else:
            team = self.waiting_players
    
        for player in team:
            if(player == old_player):
                team.remove(player)
                team.append(new_player)
                
                break
        
        if(self.captain_blue == old_player):
            self.captain_blue = new_player
        elif(self.captain_red == old_player):
            self.captain_red = new_player
                
    def finish_game(self):
        self.is_finished = True
        
        self.game_state = GameState.END_GAME
        
        #create_image.ImageHandler.end_game(self)
    
    def set_winner(self, winning_team):
        if winning_team == "1":
            self.winning_team = self.team_red
            self.losing_team = self.team_blue
        elif winning_team == "2":
            self.winning_team = self.team_blue
            self.losing_team = self.team_red
        else:
            raise ValueError("Invalid winning team identifier. Use '1' or '2'.")

    async def update_join_stage_embed(self):
        display = ""
        
        for index,player in enumerate(self.players, start = 1):
            display += str(index) + ": " + player.display_name + "\n" # " [" + str(player.elo) + " Elo]" + "\n"


        for i in range(len(self.players), self.max_players):
            display += str(i + 1) + ": " +"\n"

        embed = discord.Embed(title='Players in lobby',description=f"**Game [{self.id}] has begun! Type /join**\n```css\n{display}```", color=discord.Color.dark_orange(), timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=f'Hosted by {self.hoster.display_name}',icon_url=self.hoster.avatar.url or self.hoster.default_avatar.url)
        
        await self.embed.edit(embed=embed)
    
    def get_pick_info(self):
        def format_player_line(player, index):
            if player is None:
                return '[' + str(index + 1) + ': ' + ''.join(' ' for _ in range(20)) + ']\n'
            else:
                name = player.display_name[0:8]
                remainder = max(0, 15 - len(name))
                return '[' + str(index + 1) + ': ' + name + ''.join(' ' for _ in range(5 + remainder)) + ']\n'

        waiting_players = ''.join([
            '[' + str(i + 1) + ': ' + player.display_name + ']\n' if player != -1 else ''
            for i, player in enumerate(self.waiting_players)
        ])

        team_red = ''.join([
            format_player_line(player, i)
            for i, player in enumerate(self.team_red)
        ])

        team_blue = ''.join([
            format_player_line(player, i)
            for i, player in enumerate(self.team_blue)
        ])
        
        map_pool = ''.join([
            '[' + str(i + 1) + ': ' + map + ']\n' if map != -1 else ''
            for i, map in enumerate(self.map_pool)
        ])

        return [team_red, team_blue, waiting_players, map_pool]

    def pick_random_captains(self):
        captain_red = random.choice(self.waiting_players)
        
        self.waiting_players.remove(captain_red)
        
        captain_blue = random.choice(self.waiting_players)

        self.waiting_players.remove(captain_blue)
       
        self.team_red.append(captain_red)
        self.team_blue.append(captain_blue)
        
        return [captain_blue,captain_red]
    
    async def update_pick_stage_embed(self):
        print("Pick stage")
        
        if(not self.captain_blue and not self.captain_red):
            self.captain_blue, self.captain_red = self.pick_random_captains()
            self.player_turn = self.captain_red
        
        accent = ""
        print(self.player_turn.display_name)
        if self.player_turn.mention == self.captain_blue.mention: accent = 'ini'
        else: accent = 'css'
        
        embed = discord.Embed(title='5v5',color=discord.Color.dark_orange(), timestamp=datetime.datetime.utcnow())
        
        game_info = self.get_pick_info()
    
        team_red = game_info[0]
        team_blue = game_info[1]
        waiting_players = game_info[2]
        map_pool = game_info[3]
   
        
        if len(self.waiting_players) != 0:
            embed.add_field(name="Remaning Pick Pool", value=f"```{accent}\n{waiting_players}```", inline=True)

        if self.game_state == GameState.MAP_PICK_STAGE:
            embed.add_field(name="Remaining Map Pool",value=f"```{accent}\n{map_pool}```", inline=True)

        embed.add_field(name="Game Info", value=f"Host: ***{self.hoster.display_name}***\nTeam Red Captain: ***{self.captain_red.display_name}***\nTeam Blue Captain: ***{self.captain_blue.display_name}***\nMap: ***TBD***\nTurn: {self.player_turn.mention}", inline=True)
       
        embed.add_field(name="Team Red", value=f"```md\n{team_red}```", inline=False)
        embed.add_field( name=f"Team Blue", value=f"```ini\n{team_blue}```", inline=False)
        
        await self.embed.edit(embed=embed)

    async def update_player_roles(self, remove = False):
        for red_player,blue_player in zip(self.team_red,self.team_blue):      
            try:
                if(not remove):
                    await red_player.add_role(settings.get_team_red_roles()[str(self.channel.id)])
                    await blue_player.add_role(settings.get_team_blue_roles()[str(self.channel.id)])
                else:
                    await red_player.remove_role(settings.get_team_red_roles()[str(self.channel.id)])
                    await blue_player.remove_role(settings.get_team_blue_roles()[str(self.channel.id)])
                    
            except Exception as e:
                print(e)
       
    async def move_players_into_vc(self):
        voice_red = await bot.fetch_channel(settings.get_team_red_channels()[str(self.channel.id)])
        voice_blue = await bot.fetch_channel(settings.get_team_blue_channels()[str(self.channel.id)])

        for red_player,blue_player in zip(self.team_red,self.team_blue):      
            try:
                await red_player.move_to(voice_red)
            except Exception as e:
                print(e)
                
            await asyncio.sleep(1)
            
            try:
                await blue_player.move_to(voice_blue)
            except Exception as e:
                print(e)
    
                
    async def move_players_into_queue(self):
        queue_vc = await bot.fetch_channel(settings.get_queue_channels()[str(self.channel.id)])
        await self.update_player_roles(remove = True)
        for player in self.players:
            try:
                await player.move_to(queue_vc)
            except Exception as e:
                print(e)
                
            await asyncio.sleep(1)
            
    async def update_play_stage_embed(self):
        await self.embed.delete()
        image = imageHandler.generate_start_image(self)
        self.start_image = await self.channel.send(file=image)
        
        await self.start_game()
        
     
    async def start_game(self):
        await self.move_players_into_vc()
        
        await self.update_player_roles()
    
        self.server = await serverManager.setup_server(self.players, self.map, legacy = self.channel.id in settings.get_legacy_servers())
        
        

        
class GameMng:
    def __init__(self):
        self.running_games: list[Game] = []
        self.finished_games: list[Game] = []
    
    def get_game(self, channel) -> Game:
        for game in self.running_games:
            if(game.channel == channel):
                return game
                       
        return None
    
    def add_game(self, host,channel) -> Game:
        game = Game(host, channel, len(self.finished_games) + len(self.running_games) + 1)
        
        self.running_games.append(game)
        
        return game
    
    def remove_game(self, game: Game):
        self.running_games.remove(game)
    
    def generate_end_image(self, game: Game) -> [discord.File]:
        return imageHandler.generate_end_game_image(game)
    
    async def finish_game(self, game: Game):
        game.finish_game()
        
        self.running_games.remove(game)
        self.finished_games.append(game)
        
        await game.move_players_into_queue()
        
        game.server.available = True
        
    async def update_embed(self, game: Game):
        if game.game_state == GameState.JOIN_STAGE:
            await game.update_join_stage_embed()
        elif game.game_state == GameState.TEAM_PICK_STAGE or game.game_state == GameState.MAP_PICK_STAGE:
            await game.update_pick_stage_embed() 
        elif game.game_state == GameState.PLAY_STAGE:
            await game.update_play_stage_embed()

        
GameManager = GameMng()