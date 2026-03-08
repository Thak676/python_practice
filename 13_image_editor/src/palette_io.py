def save_palette(colors, filename, name="Untitled Palette"):
    """
    Saves a list of colors to a GIMP Palette (.gpl) file.
    
    Args:
        colors: List of/pygame.Color objects or (r, g, b) tuples.
        filename: Path to save the .gpl file.
        name: Name of the palette to write in the header.
    """
    with open(filename, 'w') as f:
        f.write("GIMP Palette\n")
        f.write(f"Name: {name}\n")
        f.write("Columns: 4\n")
        f.write("#\n")
        
        for color in colors:
            # Handle both pygame.Color objects and tuples
            if hasattr(color, 'r'):
                r, g, b = color.r, color.g, color.b
            else:
                r, g, b = color[0], color[1], color[2]
                
            f.write(f"{r:3d} {g:3d} {b:3d}\tUntitled\n")

def load_palette(filename):
    """
    Loads colors from a GIMP Palette (.gpl) file.
    
    Returns:
        List of (r, g, b) tuples.
    """
    colors = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        
        # Skip header until '#' or color data starts
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip() == '#':
                start_idx = i + 1
                break
            # Some gpl files might not have the '#' separator
            # Heuristic: if line starts with a number, it's likely color data
            parts = line.split()
            if len(parts) >= 3 and parts[0].isdigit():
                start_idx = i
                break
                
        for i in range(start_idx, len(lines)):
            line = lines[i].strip()
            if not line:
                continue
                
            parts = line.split()
            if len(parts) >= 3:
                try:
                    r = int(parts[0])
                    g = int(parts[1])
                    b = int(parts[2])
                    colors.append((r, g, b))
                except ValueError:
                    continue
                    
    return colors
