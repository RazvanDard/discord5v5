from dataclasses import dataclass
import discord 
import json
from settings_setup.setup import *
from math import pow,floor,ceil
import datetime
class EloSystem:
    def __init__(self, K=32, base_rating=1500, performance_factor=400):
        self.K = K
        self.base_rating = base_rating
        self.performance_factor = performance_factor
    
    def calculate_expected(self, player_rating, opponent_avg_rating):
        return 1 / (1 + pow(10, (opponent_avg_rating - player_rating) / self.performance_factor))
    
    def update_player_elo(self, selected_player, winning_team, losing_team):
        winning_team_avg_elo = sum(playerManager.get_player(player).rating for player in winning_team) / len(winning_team)
        losing_team_avg_elo = sum(playerManager.get_player(player).rating for player in losing_team) / len(losing_team)
        
        elo_change = 0
        
        if selected_player in winning_team:
            expected_win = self.calculate_expected(playerManager.get_player(selected_player).rating, losing_team_avg_elo)
            rating_change = self.K * (1 - expected_win)
            playerManager.get_player(selected_player).rating += round(rating_change)
            elo_change = ceil(rating_change)
            
        
        if selected_player in losing_team:
            expected_lose = self.calculate_expected(playerManager.get_player(selected_player).rating, winning_team_avg_elo)
            rating_change = self.K * (0 - expected_lose)
            playerManager.get_player(selected_player).rating += round(rating_change)
            elo_change = floor(rating_change)
            
            playerManager.get_player(selected_player).win_streak = 0
            playerManager.get_player(selected_player).games_lost += 1
        

        return elo_change

eloSystem = EloSystem(K=40, base_rating=1000, performance_factor=400)

@dataclass
class Player:
    discord_user: discord.User = None
    rating: int = 1000
    leaderboard_rank: int = 0
    games_played: int = 0
    games_won: int = 0
    games_lost: int = 0
    win_streak: int = 0
    blacklist_time: datetime.datetime = None

    def __init__(self, discord_user):
        self.discord_user = discord_user
    
    def update_stats(self, game):
        if self.discord_user in game.winning_team:
            self.win_streak += 1
            self.games_won += 1
            self.games_played += 1
        elif self.discord_user in game.losing_team:
            self.win_streak = 0
            self.games_lost += 1
            self.games_played += 1
            
    def calculate_elo(self, game):
        
        self.update_stats(game)
        
        return eloSystem.update_player_elo(self.discord_user, game.winning_team, game.losing_team)
   
    def has_perms(self,roles):
        player_roles = [role.id for role in self.discord_user.roles]
        
        if any(role in player_roles for role in roles):
            return True
    
    def has_admin_perms(self):
        return self.has_perms(settings.get_admin_roles())
    
    def has_mod_perms(self):
        return self.has_perms(settings.get_mod_roles()) or self.has_admin_perms()
    
    def has_hoster_perms(self):
        return self.has_perms(settings.get_hoster_roles()) or self.has_admin_perms() or self.has_mod_perms()
    
    def add_elo(self, amount):
        self.rating += amount
    
    def remove_elo(self, amount):
        self.rating -= amount
        
    def add_win(self):
        self.games_played += 1
        self.games_won += 1
        self.win_streak += 1
    
    def remove_win(self):
        self.games_played -= 1
        self.games_won -= 1
        self.win_streak -= 1
    
    def add_lose(self):
        self.games_played += 1
        self.games_lost += 1
        self.win_streak = 0
    
    def remove_lose(self):
        self.games_played -= 1
        self.games_lost -= 1
        self.win_streak = 0
    
   
class PlayerManager:
    def __init__(self):
        self.players = {}  # Dictionary to store players by their discord user ID
    
    def add_player(self, discord_user):
        if discord_user.id not in self.players:
            self.players[discord_user.id] = Player(discord_user)
            return True
            
        return False
    
    def get_player(self, discord_user):
        return self.players.get(discord_user.id, None)
    
    def update_leaderboard(self):
        sorted_players = sorted(self.players.values(), key=lambda player: player.rating, reverse=True)
        for rank, player in enumerate(sorted_players, start=1):
            player.leaderboard_rank = rank
    
    def get_leaderboard(self):
        return sorted(self.players.values(), key=lambda player: player.rating, reverse=True)
    
    def reset_leaderboard(self):
        for player in self.players.values():
            player.rating = 1000
            player.games_played = 0
            player.games_won = 0
            player.games_lost = 0
            player.win_streak = 0
            
    def save_players_to_json(self, filename):
        player_data = []
       
        for player in self.players.values():
                
            blacklist_timestamp = None
            if player.blacklist_time:
                blacklist_timestamp = int(player.blacklist_time.timestamp())  # Serialize timestamp
                
            player_data.append({
                "id": player.discord_user.id,
                "rating": player.rating,
                "leaderboard_rank": player.leaderboard_rank,
                "games_played": player.games_played,
                "games_won": player.games_won,
                "games_lost": player.games_lost,
                "win_streak": player.win_streak,
                "blacklist_time": blacklist_timestamp
            })
        
        with open(filename, "w") as json_file:
            json.dump(player_data, json_file, indent=4)
    
    def fetch_discord_member(self,id):
        guild = bot.get_guild(settings.get_server_id())
        
        for member in guild.members:
            if member.id == id:
                return member
            
    async def load_players_from_json(self, filename, *, debug = False):
        try:
            with open(filename, "r") as json_file:
                player_data = json.load(json_file)
                for data in player_data:
                    
                    try:
                        discord_user = self.fetch_discord_member(int(data["id"]))
                        player = Player(discord_user)
                        player.rating = data["rating"]
                        player.leaderboard_rank = data["leaderboard_rank"]
                        player.games_played = data["games_played"]
                        player.games_won = data["games_won"]
                        player.games_lost = data["games_lost"]
                        player.win_streak = data["win_streak"]
                        
                        blacklist_timestamp = data.get("blacklist_time")
                        
                        if blacklist_timestamp is not None:
                            blacklist_time = datetime.datetime.fromtimestamp(blacklist_timestamp)
                            player.blacklist_time = blacklist_time
                        else:
                            player.blacklist_time = None

                        self.players[player.discord_user.id] = player
                        
                        if(debug):
                            print(f"Loaded player data for {player.discord_user.display_name}")
                    except:
                        if(debug):
                            print(f"Could not load player data for {data['id']}")
                            
        except FileNotFoundError:
            raise Exception("No player data found. Starting with an empty player list.")
        
        if(debug):
            print(f"Loaded {len(self.players)} players from json file.")
    
    def add_players_from_guild(self, guild, *, debug = False):
        for member in guild.members:
            if not member.bot:
                if(self.add_player(member) and debug):
                    print(f"Added {member.display_name} to player list.")
                
                
playerManager = PlayerManager()