import pygame
import random
import os

def generate_grass_tile(size=(16, 16), save_path="grass_tile.png"):
    # Initialize pygame modules needed for image manipulation
    # We don't need a display for this
    pygame.display.init()
    
    surface = pygame.Surface(size)
    
    # Base grass color (a nice medium green)
    # RGB: 34, 177, 76 is a good starting point
    base_r, base_g, base_b = 34, 177, 76
    surface.fill((base_r, base_g, base_b))
    
    # Add simple noise for texture
    width, height = size
    
    # Lock the surface for pixel access
    pixel_array = pygame.PixelArray(surface)
    
    for x in range(width):
        for y in range(height):
            # Randomize the color slightly
            noise = random.randint(-15, 15)
            
            # Apply noise and clamp values
            r = max(0, min(255, base_r + noise))
            g = max(0, min(255, base_g + noise))
            b = max(0, min(255, base_b + noise))
            
            pixel_array[x, y] = (r, g, b)
            
    # Unlock the surface
    del pixel_array 
    
    # Save the file
    pygame.image.save(surface, save_path)
    print(f"Generated grass tile: {save_path}")

if __name__ == "__main__":
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Output file path
    output_file = os.path.join(current_dir, "grass_01.png")
    
    generate_grass_tile(save_path=output_file)
