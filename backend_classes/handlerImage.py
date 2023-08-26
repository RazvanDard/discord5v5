import discord
from PIL import Image, ImageDraw, ImageFont
import os
from backend_classes.playerData import *
class ImageHandler:
    def __init__(self):    
        self.path = os.path.abspath("assets/images")
        self.font = ImageFont.truetype("arial.ttf", 15)
    
    def open_image(self, image_path):
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        return image, draw
    
    def generate_start_image(self, game) -> discord.File:
        image_path = os.path.join(self.path, "startgame-5v5.png")
        output_path = os.path.join(self.path, "image.png")
        
        try:
            image, draw = self.open_image(image_path)
        except Exception as e:
            print(f"Error opening image: {e}")
            
        team_red = game.team_red
        team_blue = game.team_blue
        
        y_offset = 55
        
        def draw_team_names(team, x_position):
            counter = 0
            for player in team:
                y_position = y_offset + 24 * counter
                if counter == 4:
                    y_position -= 1
                draw.text((x_position, y_position), player.display_name[0:14], (255, 255, 255, 255), font=self.font)
                counter += 1
        
        draw_team_names(team_red, 13)
        draw_team_names(team_blue, image.size[0] / 2 + 63)
        
        hoster_text = f"Hoster: {game.hoster.display_name}"
        
        hoster_text_width = self.font.getlength(hoster_text)
        x_centered = image.size[0] / 2 - hoster_text_width / 2
        
        draw.text((x_centered, 180), hoster_text, (255, 255, 255), font=self.font)
        
        image.save(output_path)
        
        return discord.File(output_path)
    
    def generate_end_game_image(self, game) -> [discord.File]:
        im, draw = self.open_image(os.path.join(self.path, "results-5v5.png"))

        def draw_player_info(players):
            text_start_y = 67
            text_start_x = 10
            text_spacing = 50
            text_start_x_2 = 110
            
            for i, player in enumerate(players):
                y_position = text_start_y + text_spacing * i
                
                elo_change = playerManager.get_player(player).calculate_elo(game)
                
                draw.text((text_start_x, y_position), player.display_name[:12], (255, 255, 255), font=self.font)
                draw.text((im.size[0] / 2 + text_start_x_2, y_position), f" {elo_change}", (255, 255, 255), font=self.font)

        draw_player_info(game.winning_team)
        
        im.save("win.png")
        
        win_img = discord.File('win.png')

        im, draw = self.open_image(os.path.join(self.path, "results-5v5.png"))
          
        draw_player_info(game.losing_team)
        
        im.save("lose.png")
        
        lose_img = discord.File('lose.png')

        return [win_img, lose_img]

    

# Usage example
imageHandler = ImageHandler()

