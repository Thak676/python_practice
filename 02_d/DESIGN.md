# Game Design Document — Vampire Survivors Inspired Game

## High-level concept

Top-down horde-survival like the game Vampire Survivors. Player moves; weapons fire automatically. Survive as long as
possible against infinitely scaling enemy waves. Pixel-art aesthetic, low-res framebuffer
scaled to screen (already in place).

---

## Tech baseline (what already exists)

| Thing | Detail |
|---|---|
| Framebuffer | 256×160 px, scaled to 1760×1024 |
| Library | `l01`: `init`, `pe`, `update_screen`, `IR` (Image_Rect), `global_vars.keys` |
| Player sprite | `m_03_02.png`, `IR` object, 8-directional keyboard move |
| Background | Tiling 4-variant flipped bg, smooth camera follow |

---

## Core loop (one game session)

```
spawn enemies → player moves → weapons fire → enemies die → xp gems drop
→ player collect gems → level up → choose upgrade → repeat until death
```

Each session runs a fixed-length timer (e.g. 20 minutes). Surviving to the end is a win.

---

## Player

- **Speed**: 1 px/frame on the framebuffer (already implemented)
- **HP**: starts at 10, shown as a bar
- **Invincibility frames**: none — damage stacks every frame an enemy overlaps the player
- **Facing**: left/right flip (already implemented); use for weapon aim bias
- **Knockback**: on hit, enemies are pushed ~8 px away from the player's centre; this naturally limits damage stacking
- **Screen shake**: 8-frame shake (±2 px random offset) when the player takes damage

---

## Enemies

### Basic slime (first enemy type)
- Spawns at a random point on the perimeter of the camera view + margin
- Moves straight toward player at fixed speed (0.4 px/frame)
- HP: 1, Damage: 1, XP drop: 1 gem

### Scaling rules (simple)
- Every 30 seconds, spawn rate increases by 20%
- Every 60 seconds, a faster/tougher variant unlocks

### Boss enemy
- Spawns every 5 minutes (fixed schedule, not random)
- Telegraphed by a full-screen warning flash 3 seconds before appearance
- Much larger sprite (placeholder: 12×12 square), high HP (50), slow speed (0.2)
- Drops a chest on death → guaranteed specific upgrade (not random)

---

## Weapons (auto-fire, no player input)

### Dagger (starter weapon)
- Fires every 60 frames in the direction the player last moved / is facing
- Projectile travels 80 px then disappears
- Damage: 1

### Orbit orb (first unlock)
- 1 orb orbiting the player at radius 20 px, full rotation every 120 frames
- Damage: 1 per contact, 30-frame hit cooldown per enemy

### Whip
- Short-range arc in front of the player, hits all enemies in a cone
- Fires every 90 frames; cone angle ~60°, range ~30 px
- Damage: 2 (rewards staying close to enemies)

### Boomerang
- Projectile travels 60 px outward then reverses back to player
- Hits enemies on both passes; expires on return or after 1 hit per pass
- Damage: 1 per hit

### Area pulse
- Periodic damage burst in a radius (~25 px) around the player
- Fires every 120 frames; no projectile, instant damage to all enemies in range
- Damage: 1

---

## XP & leveling

- Gems on the ground; auto-collected when player walks within 8 px
- XP thresholds: 5, 12, 22, 35, … (triangular growth)
- On level-up: pause, show 3 random upgrade cards, player picks with arrow keys + space

---

## Upgrades (initial pool)

| Upgrade | Effect |
|---|---|
| Dagger cooldown −10% | fires faster |
| Dagger damage +1 | |
| +1 orb | add another orbiting orb |
| +1 max HP | also heals 1 |
| Move speed +10% | |
| Magnet | doubles gem pickup radius |
| Unlock Whip | one-time; filtered from pool once active |
| Unlock Boomerang | one-time; filtered from pool once active |
| Unlock Area Pulse | one-time; filtered from pool once active |

### Upgrade filtering & weapon leveling

- The player can hold **at most 3 weapons**. Weapon unlock cards are filtered from the pool once the slot cap is reached.
- **One-time unlocks** are also removed from the pool once acquired (filtered by an `available` predicate on each POOL entry).
- After a weapon is unlocked, subsequent level-ups offer **weapon-specific upgrades** for it instead of the unlock card. Implemented for: Whip (faster, +1 dmg, wider arc), Orb (+1 orb).
- Weapon leveling for Dagger (beyond the existing stat upgrades) is not yet separated into its own tier.

## Passive items & synergies

Chests (boss drops) grant passive items rather than the normal upgrade pool.

| Item | Effect |
|---|---|
| Mirror | doubles orb count |
| Sharpening stone | all projectile damage +1 |
| Adrenaline | speed +20% when HP < 30% |

---

## Meta

- **High score** — on death or win, write `time_survived` (seconds) and `level` to `scores.txt`
- **Start menu** — title screen with `[Space] to start`; future: character select (sprite swap)

---

## Data / entity model

```
Player:   x, y, hp, max_hp, speed, xp, level, iframes, weapons[]
Enemy:    x, y, hp, speed, damage, xp_value
Projectile: x, y, vx, vy, damage, life (frames remaining)
Gem:      x, y, value
```

All entities are plain objects (e.g. `SimpleNamespace` or small dataclasses). Lists of
enemies/projectiles/gems are iterated each frame and filtered to remove dead ones.

---

## Rendering order (back → front, all onto `fb`)

1. Tiled background
2. XP gems
3. Enemies
4. Player
5. Projectiles / orbs
6. HUD (HP bar, XP bar, timer) — drawn directly on `fb`, top layer

---

## HUD

- HP bar: top-left, red, 40 px wide
- XP bar: bottom, full width, blue
- Timer: top-right, white text (pygame.font small)
- Weapon slots: bottom-right, up to 3 small icons (placeholder squares) showing active weapons; empty slots shown as dim outlines

---

## File / module plan

```
src/
  main.py          — game loop, init, top-level state
  player.py        — Player class / update / draw
  enemies.py       — Enemy class / spawning / update
  weapons.py       — weapon definitions, projectile update
  gems.py          — Gem class, collection logic
  hud.py           — draw_hud(fb, player, timer)
  upgrade.py       — upgrade card screen
```

---

## Implementation order (suggested)

1. Enemy spawning + movement toward player
2. Player HP + damage + iframes
3. Dagger projectile
4. XP gem drop + collection + level bar
5. Level-up screen + upgrade cards
6. Orbit orb weapon
7. HUD polish + timer + win/lose screens

---

## Art constraints

- All sprites should fit the 256×160 pixel canvas — keep them tiny (≤ 16×16 for enemies)
- Reuse the existing 4-variant tiling background
- Prefer existing assets in `data/` before adding new ones

---

## Meta-game: Gold & Persistent Upgrades

### Overview
Between runs the player visits a **Shop** screen. Gold earned during runs persists across sessions (saved to disk alongside the high score). Spending gold unlocks or improves passive bonuses that apply to every future run — not just the current one.

### Earning gold
- Enemies drop a small chance of a gold coin on death (e.g. 10% chance, 1 coin each)
- Boss kills guarantee a bonus gold drop (e.g. 5 coins)
- Surviving longer gives a time bonus: `floor(minutes_survived) * 2` coins awarded at end of run (win or death)
- Gold is displayed on the HUD (top-right, near the timer) during a run

### Shop screen
Shown automatically after the game-over / win screen, before returning to the start menu.
- Displays current gold balance and a fixed list of purchasable upgrades
- Navigation with arrow keys; confirm with Space/Enter; exit with Escape (unspent gold is kept)
- Each upgrade shows its current rank, max rank, cost to next rank, and effect description
- Purchased ranks persist in `meta.json` alongside gold balance

### Persistent upgrade pool (initial)

| Upgrade | Max rank | Cost per rank | Effect per rank |
|---|---|---|---|
| Starting HP | 5 | 10 | +2 max HP at run start |
| Starting Speed | 3 | 15 | +5% move speed at run start |
| Gold Finder | 3 | 20 | +10% gold drop chance |
| XP Boost | 4 | 12 | +5% XP gain per rank |
| Dagger Mastery | 3 | 25 | Dagger starts with +1 damage |
| Extra Life | 1 | 50 | Revive once per run with 50% HP |

### Data model
```
meta.json
{
  "gold": 120,
  "high_score": { "time_seconds": 340, "level": 8 },
  "upgrades": {
    "starting_hp": 2,
    "starting_speed": 1,
    "gold_finder": 0,
    "xp_boost": 0,
    "dagger_mastery": 0,
    "extra_life": 0
  }
}
```

### Application to runs
At the start of each run, `meta.json` is read and bonus stats are applied to the Player and Dagger before the loop starts. This keeps run initialisation explicit and easy to test.

### Files to add
```
src/
  meta.py      — load/save meta.json, apply bonuses to player/weapons
  shop.py      — blocking shop screen (same pattern as menu.py / upgrade.py)
```

Gold coins during a run can be a second collectible type alongside gems, sharing the same collect-on-proximity model as `Gem`.
