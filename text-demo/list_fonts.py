import pygame

# Initialize the font module
pygame.font.init()

# Get the list of all available fonts
# The names are returned in lowercase and without spaces
font_list = pygame.font.get_fonts()

# Print the list of fonts
for font_name in font_list:
    print(font_name)
