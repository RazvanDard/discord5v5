import json
from discord.ext import commands
import discord

class Settings:
    def __init__(self, config_file_path):
        with open(config_file_path, 'r') as f:
            self.config = json.load(f)

    def get(self, category: str, value: str):
        return self.config[category][value]

    def get_bot_token(self) -> str:
        return self.get("global", "bot_token")
    
    def get_server_id(self) -> int:
        return int(self.get("global", "server_id"))

    def get_server_info(self, server_id: int) -> dict:
        return self.get("global", f"server{server_id}")
    
    def get_logo(self) -> str:
        return self.get("global", "logo")

    def get_server_count(self) -> int:
        return int(self.get("global", "server_count"))
    
    def get_cmd_prefix(self) -> str:
        return self.get("global", "command_prefix")
    
    def get_log_channel_id(self) -> int:
        return self.get("global", "log_channel_id")

    def get_legacy_servers(self) -> list[int]:
        return self.get("global", "legacy_hosts")
    def get_hoster_roles(self) -> list:
        return self.get("global", "hoster_perms")

    def get_2v2_maps(self) -> list:
        return self.get("global", "2v2maps")

    def get_5v5_maps(self) -> list:
        return self.get("global", "5v5maps")

    def get_mod_roles(self) -> list:
        return self.get("global", "mod_perms")

    def get_admin_roles(self) -> list:
        return self.get("global", "admin_perms")

    def get_5v5_channels(self) -> list:
        return self.get("global", "5v5_hosts")

    def get_queue_channels(self) -> list:
        return self.get("global", "queue_channels")

    def get_hosting_channels(self) -> list:
        return self.get("global", "hosting_channels")
    
    def get_team_red_channels(self) -> dict:
        return self.get("global", "team_red_channels")

    def get_team_blue_channels(self) -> dict:
        return self.get("global", "team_blue_channels")

    def get_team_red_roles(self) -> dict:
        return self.get("global", "team_red_roles")

    def get_team_blue_roles(self) -> dict:
        return self.get("global", "team_blue_roles")

settings = Settings('setup.json')

bot = commands.Bot(command_prefix=settings.get_cmd_prefix(), intents=discord.Intents().all())