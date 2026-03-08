
def generate_upgrades():
    options = [
        {"name": "Move Speed +10%", "key": "move_speed", "value": 1.1, "type": "mult"},
        {"name": "Fire Rate +10%", "key": "fire_rate", "value": 0.9, "type": "mult"}, # Lower is faster (frames)
        {"name": "Proj Speed +10%", "key": "projectile_speed", "value": 1.1, "type": "mult"},
        {"name": "Pickup Range +20%", "key": "pickup_radius", "value": 1.2, "type": "mult"},
        {"name": "Heal 20 HP", "key": "heal", "value": 20, "type": "add"}
    ]
    # Pick 3 unique upgrades
    return random.sample(options, 3)
    