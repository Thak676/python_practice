
import pygame
from pygame.locals import *

from Circle import Circle
from palette_io import save_palette, load_palette

SCREEN_W = 1920
SCREEN_H = 1080
WORLD_W = 16
WORLD_H = 16

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock = pygame.time.Clock()

m = Circle(20, 20, 2, (14, 240, 240, 255))

speed = 0.1
m_speed = 0.2
max_vel = 10

fb1 = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)
fb2 = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)
fb2.fill((0, 0, 0, 255)) # Ensure fb2 starts with black background
fb_right_panel = pygame.Surface((420, 1080 - 420))
fb_top_right_panel = pygame.Surface((420, 420))
fb_left_panel = pygame.Surface((420, 1080))
zoom_level = 1.0
zoom_speed = 0.1
pan_x = 0
pan_y = 0
pan_speed = 2
show_grid = False

# Palette logic
current_palette = []
try:
    current_palette = load_palette("palette.gpl")
    print(f"Loaded {len(current_palette)} colors from palette.gpl")
except FileNotFoundError:
    print("palette.gpl not found, starting with empty palette")

def draw_palette_panel(surface, palette):
    surface.fill((30, 30, 30))
    cols = 8
    swatch_size = 40
    gap = 5
    start_x = 10
    start_y = 10
    
    for i, color in enumerate(palette):
        row = i // cols
        col = i % cols
        x = start_x + col * (swatch_size + gap)
        y = start_y + row * (swatch_size + gap)
        pygame.draw.rect(surface, color, (x, y, swatch_size, swatch_size))

draw_palette_panel(fb_right_panel, current_palette)

# Initialize color picker
draw_color = (255, 0, 0, 255)
picker_hue = 0
picker_sat = 100
picker_val = 100

def update_color_picker(surface, hue):
    # SV Square (420x420)
    base = pygame.Surface((420, 420))
    c = pygame.Color(0)
    c.hsva = (hue, 100, 100, 100)
    base.fill(c)
    
    sat_grad = pygame.Surface((420, 420), pygame.SRCALPHA)
    # Horizontal white to transparent (handles saturation)
    for x in range(420):
        alpha = 255 - int((x / 420.0) * 255)
        pygame.draw.line(sat_grad, (255, 255, 255, alpha), (x, 0), (x, 420))
    
    val_grad = pygame.Surface((420, 420), pygame.SRCALPHA)
    # Vertical transparent to black (handles value)
    for y in range(420):
        alpha = int((y / 420.0) * 255)
        pygame.draw.line(val_grad, (0, 0, 0, alpha), (0, y), (420, y))
        
    base.blit(sat_grad, (0, 0))
    base.blit(val_grad, (0, 0))
    surface.blit(base, (0, 0))
    
    # Hue slider (bottom strip, 50px high)
    for x in range(420):
        h = int((x / 420.0) * 360)
        c = pygame.Color(0)
        c.hsva = (h, 100, 100, 100)
        pygame.draw.line(surface, c, (x, 420), (x, 470))

update_color_picker(fb_left_panel, picker_hue)

def bucket_fill(surface, start_pos, fill_color):
    try:
        target_color = surface.get_at(start_pos)
    except IndexError:
        return
        
    if target_color == fill_color:
        return

    w, h = surface.get_size()
    stack = [start_pos]
    
    while stack:
        x, y = stack.pop()
        
        if not (0 <= x < w and 0 <= y < h):
            continue
            
        try:
            if surface.get_at((x, y)) == target_color:
                surface.set_at((x, y), fill_color)
                stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
        except IndexError:
            pass

while True:
  # get input
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      exit()
    if event.type == KEYDOWN:
      if event.key == K_g:
          show_grid = not show_grid
      if event.key == K_s and pygame.key.get_mods() & KMOD_CTRL:
          # Collect unique colors from fb2
          unique_colors = set()
          for x in range(fb2.get_width()):
              for y in range(fb2.get_height()):
                  try:
                      # Ignore fully transparent pixels if any (though currently initialized to black opaque)
                      c = fb2.get_at((x, y))
                      if c.a > 0:
                          unique_colors.add(c[:3]) 
                  except IndexError:
                      pass
          
          # Convert set to sorted list for consistent output if desired
          palette_list = sorted(list(unique_colors))
          current_palette = palette_list

          print(f"saving palette with {len(palette_list)} colors to palette.gpl")
          save_palette(palette_list, "palette.gpl", "Canvas Palette")
          draw_palette_panel(fb_right_panel, current_palette)

      if event.key == K_SPACE:
          print("saving fb2 to file")
          pygame.image.save(fb2, "fb2_dump.png")
      if event.key == K_b:
          mpos = pygame.mouse.get_pos()
          if mpos[0] > 420 and mpos[0] < 1500:
              rel_x = mpos[0] - offset_x
              rel_y = mpos[1] - offset_y
              if scaled_w > 0 and scaled_h > 0:
                  x = int((rel_x / scaled_w) * WORLD_W)
                  y = int((rel_y / scaled_h) * WORLD_H)
                  flood_fill(fb2, (x, y), draw_color)
    if event.type == MOUSEWHEEL:
        if event.y > 0:
            zoom_level += zoom_speed
        elif event.y < 0:
            zoom_level = max(0.1, zoom_level - zoom_speed)
            
  keys = pygame.key.get_pressed()
  
  if keys[K_UP]:
      pan_y += pan_speed
  if keys[K_DOWN]:
      pan_y -= pan_speed
  if keys[K_LEFT]:
      pan_x += pan_speed
  if keys[K_RIGHT]:
      pan_x -= pan_speed

  screen.fill((20,20,20))
  fb1.fill((0, 0, 0, 0)) # Make fb1 transparent so it doesn't cover fb2
  fb_top_right_panel.fill(draw_color) # Show selected color on top right panel

  #update
  m.vel.x += m_speed * ((keys[K_d]) - (keys[K_a]))
  m.vel.y += m_speed * ((keys[K_s]) - (keys[K_w]))

  if m.vel.length() > max_vel:
    m.vel.scale_to_length(max_vel)
    
  m.pos += m.vel * speed

  if m.x > WORLD_W:
    m.x = 0
  elif m.x < 0:
    m.x = WORLD_W
    
  if m.y > WORLD_H:
    m.y = 0
  elif m.y < 0:
    m.y = WORLD_H

  #draw
  m.draw(fb1)

  # Update mouse interaction for zoom
  # We need to map screen coordinates back to fb2 coordinates considering zoom and centering
  # Center of fb2 display area is (420 + 1080/2, 1080/2) = (960, 540)
  # Scaled size is (1080 * zoom_level, 1080 * zoom_level)
  # Top-left of zoomed image: 960 - (1080 * zoom_level)/2, 540 - (1080 * zoom_level)/2
  
  display_center_x = 420 + 1080 // 2 + pan_x
  display_center_y = 1080 // 2 + pan_y
  scaled_w = 1080 * zoom_level
  scaled_h = 1080 * zoom_level
  offset_x = display_center_x - scaled_w // 2
  offset_y = display_center_y - scaled_h // 2

  mouse_buttons = pygame.mouse.get_pressed()
  if mouse_buttons[0]:
    try:
      mpos = pygame.mouse.get_pos()
      if mpos[0] > 0 and mpos[0] < 420:
          # Left Panel Interaction (Color Picker)
          if mpos[1] < 420:
              # SV Square interaction
              draw_color = fb_left_panel.get_at((mpos[0], mpos[1]))
              # Update sat/val state
              picker_sat = (mpos[0] / 420.0) * 100
              picker_val = 100 - (mpos[1] / 420.0) * 100
          elif mpos[1] < 470:
              # Hue Slider interaction
              picker_hue = int((mpos[0] / 420.0) * 360)
              update_color_picker(fb_left_panel, picker_hue)
              
              # Recompute draw_color with new hue but existing sat/val
              c = pygame.Color(0)
              c.hsva = (picker_hue, picker_sat, picker_val, 100)
              draw_color = c
      elif mpos[0] > 420 and mpos[0] < 1500:
        rel_x = mpos[0] - offset_x
        rel_y = mpos[1] - offset_y
        
        # Normalize to 0-1 range within the zoomed image
        norm_x = rel_x / scaled_w
        norm_y = rel_y / scaled_h
        
        if scaled_w > 0 and scaled_h > 0:
            # Map to fb2 coordinates
            fb_x = norm_x * WORLD_W
            fb_y = norm_y * WORLD_H
            
            if 0 <= fb_x < WORLD_W and 0 <= fb_y < WORLD_H:
                 fb2.set_at((int(fb_x), int(fb_y)), draw_color)
      elif mpos[0] > 1500 and mpos[1] > 420:
        # Palette pick
        pal_local_x = mpos[0] - 1500
        pal_local_y = mpos[1] - 420
        c = fb_right_panel.get_at((pal_local_x, pal_local_y))
        # Ignore background color (dark grey)
        if c != (30, 30, 30, 255):
            draw_color = c
    except:
      pass

  if mouse_buttons[2]:
    try:
      mpos = pygame.mouse.get_pos()
      if mpos[0] > 420 and mpos[0] < 1500:
        rel_x = mpos[0] - offset_x
        rel_y = mpos[1] - offset_y
        norm_x = rel_x / scaled_w
        norm_y = rel_y / scaled_h
        fb_x = norm_x * WORLD_W
        fb_y = norm_y * WORLD_H
        
        if 0 <= fb_x < WORLD_W and 0 <= fb_y < WORLD_H:
             draw_color = fb2.get_at((int(fb_x), int(fb_y)))
    except:
      pass

  # handle screen
  # fb2.blit(fb1,(0,0))
  
  # Prepare zoomed surface
  # We scale fb2 to the zoomed size
  # Note: transforming every frame can be slow if surfaces are large
  zoomed_fb2 = pygame.transform.scale(fb2, (int(scaled_w), int(scaled_h)))
  
  # Blit centered
  # We need to clip or handle if it goes out of bounds? 
  # Pygame handles blitting out of bounds fine.
  # But we want to respect the drawing area (420 to 1500).
  # Simple approach: set clip rect for screen
  screen.set_clip(pygame.Rect(420, 0, 1080, 1080))
  screen.blit(zoomed_fb2, (offset_x, offset_y))
  
  if show_grid:
      # Grid drawing logic
      # Using a dedicated surface for alpha blending lines
      grid_surface = pygame.Surface((1080, 1080), pygame.SRCALPHA)
      grid_color = (128, 128, 128, 80)
      
      # Calculate visible range
      # Relative to the VIEWPORT (which starts at x=420)
      # offset_x is relative to SCREEN x=0.
      viewport_x = 420
      viewport_w = 1080
      
      # Determine cols to draw
      # x position of col i on screen: offset_x + i * (scaled_w / WORLD_W)
      # We want x >= viewport_x and x <= viewport_x + viewport_w
      
      pixel_size_x = scaled_w / WORLD_W
      pixel_size_y = scaled_h / WORLD_H

      start_col = int((viewport_x - offset_x) / pixel_size_x)
      end_col = int((viewport_x + viewport_w - offset_x) / pixel_size_x) + 1
      
      start_col = max(0, start_col)
      end_col = min(WORLD_W, end_col + 1)
      
      start_row = int((0 - offset_y) / pixel_size_y)
      end_row = int((1080 - offset_y) / pixel_size_y) + 1
      
      start_row = max(0, start_row)
      end_row = min(WORLD_H, end_row + 1)

      for i in range(start_col, end_col + 1):
          # Correctly calculate integer positions to match pixel boundaries
          # Use round() or just int() depending on preference, int() is standard
          line_x = int(offset_x + i * pixel_size_x) - viewport_x
          if 0 <= line_x <= 1080:
              pygame.draw.line(grid_surface, grid_color, (line_x, 0), (line_x, 1080))
          
      for i in range(start_row, end_row + 1):
          line_y = int(offset_y + i * pixel_size_y)
          if 0 <= line_y <= 1080:
              pygame.draw.line(grid_surface, grid_color, (0, line_y), (1080, line_y))
      
      screen.blit(grid_surface, (420, 0))

  screen.set_clip(None) # Reset clip

  # screen.blit(pygame.transform.scale(fb1, (1080,1080)), (420,0)) # Player overlay (not zoomed? or should it handle zoom too?)
  # Assuming player overlay should also be zoomed if it 'lives' in the world.
  # But fb1 was 'player layer'.
  # For now, let's just zoom fb2 as requested.
  
  screen.blit(fb_right_panel, (1500, 280))
  screen.blit(fb_right_panel, (1500, 420))
  screen.blit(fb_top_right_panel, (1500, 0))
  screen.blit(fb_left_panel, (0, 0))
  pygame.display.flip()

