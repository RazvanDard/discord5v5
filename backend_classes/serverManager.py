import threading
import random
import valve.rcon
import discord
import string 
import asyncio
import requests
from settings_setup.setup import *

class Server:
    def __init__(self, server_id):
        self.server_info = settings.get_server_info(server_id)
        self.ip = self.server_info['ip']
        self.rcon_port = self.server_info['rcon_port']
        self.rcon_pass = self.server_info['rcon_pass']
        self.rcon_address = (self.ip, self.rcon_port)
        self.server_id = server_id
        self.password = None
        self.available = True
        self.legacy = self.server_info['legacy']

    def start_password_change(self):
        self.generate_random_password()
        self.update_remote_password()

    def generate_random_password(self):
        letters = string.ascii_uppercase
        self.password = ''.join(random.choice(letters) for _ in range(6))
        
        return self.password

    def update_remote_password(self):
        
        with valve.rcon.RCON(self.rcon_address, password = self.rcon_pass) as rcon:
            response = rcon.execute(f"sm_cvar sv_password {self.password}")
            print(response.text)

    async def start_map_change(self, new_map):
    
        with valve.rcon.RCON(self.rcon_address,password = self.rcon_pass) as rcon:
            response = rcon.execute(f"sm_map {new_map}")
            print(response.text)
            
        await asyncio.sleep(7)
        
        with valve.rcon.RCON(self.rcon_address,password = self.rcon_pass) as rcon:
            response = rcon.execute("sm_setup")
            print(response.text)

    def get_map_image_url(self):
        # Define map-to-image URL mapping here
        # Return the appropriate image URL based on the map
        pass
            
    async def send_server_embed(self, players):
        embed = await self.get_server_embed()
        
        for player in players:
            player.send(embed=embed)
            await asyncio.sleep(1)
        
    async def get_server_embed(self):
        url = self.get_short_url(f'steam://connect/{self.ip}:{self.rcon_port}/{self.password}')
        embed = discord.Embed(title='', color=discord.Color.dark_orange())
        embed.description = f"[BG5v5 #{self.server_id}]({url})"
        embed.set_footer(text='BG5v5', icon_url='https://i.imgur.com/fVUuelH.png')

        #embed.set_image(url=self.get_map_image_url())
        
        return embed

    def get_short_url(self, url):
        response = requests.get('https://tinyurl.com/api-create.php?url=' + url)
        return response.text
    
class ServerManager:
    def __init__(self):
        self.servers = []

    def add_server(self):
        server = Server(server_id = len(self.servers) + 1)
        self.servers.append(server)

    def start_password_change(self, server):
        server.start_password_change()

    async def start_map_change(self, server, new_map):
        await server.start_map_change(new_map)
    
    def get_server(self, server_id):
        for sv in self.servers:
            if sv.server_id == server_id:
                return sv
            
    async def setup_server(self, players, map_name, legacy = False) -> Server:
        server = self.get_available_server(legacy)
        
        await self.start_map_change(server,map_name)
        self.start_password_change(server)
        
        await server.send_server_embed(players)
        
        server.available = False
        
        return server
    
    async def send_password(self, server, player):
        await server.send_server_embed([player])
        
    def get_available_server(self, legacy):
        for server in self.servers:
            if server.available and server.legacy == legacy:
                return server
            
        return None
    

# Example usage
serverManager = ServerManager()

# Add servers using server_manager.add_server(server_data)
